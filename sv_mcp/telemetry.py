import logging
import os
from typing import Any, Callable, Awaitable

import httpx

logger = logging.getLogger(__name__)

try:
    from opentelemetry import trace  # noqa: F401 — must be module-level for patching
    _OTEL_API_AVAILABLE = True
except ImportError:
    trace = None  # type: ignore[assignment]
    _OTEL_API_AVAILABLE = False


def init_telemetry(service_name: str, service_version: str) -> None:
    if not _OTEL_API_AVAILABLE:
        return
    if os.getenv("OTEL_SDK_DISABLED", "").lower() == "true":
        return
    try:
        from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({SERVICE_NAME: service_name, SERVICE_VERSION: service_version})
        provider = TracerProvider(resource=resource)

        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
                provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
            except Exception:
                logger.debug("OTLP exporter setup failed; traces will be discarded", exc_info=True)

        trace.set_tracer_provider(provider)
        logger.debug("OTel TracerProvider initialised (service=%s, version=%s)", service_name, service_version)
    except ImportError:
        pass
    except Exception:
        logger.debug("OTel init failed; continuing without tracing", exc_info=True)


def _get_meta(ctx: Any) -> dict:
    try:
        return ctx.request_context.request.params.meta or {}
    except Exception:
        return {}


def _extract_trace_context(meta: dict):
    if not meta:
        return None
    try:
        from opentelemetry.propagate import extract
        carrier = {}
        if "traceparent" in meta:
            carrier["traceparent"] = meta["traceparent"]
        if "tracestate" in meta:
            carrier["tracestate"] = meta["tracestate"]
        return extract(carrier) if carrier else None
    except Exception:
        return None


def _get_client_info(ctx: Any):
    try:
        info = ctx.request_context.session.client_params.clientInfo
        return info.name, info.version
    except Exception:
        return None, None


def _record_span_error(span: Any, error_type: str) -> None:
    try:
        span.set_attribute("error.type", error_type)
    except Exception:
        pass
    try:
        from opentelemetry.trace import Status, StatusCode
        span.set_status(Status(StatusCode.ERROR))
    except Exception:
        pass


def _http_status_to_error_type(status_code: int) -> str:
    if status_code in (401, 403):
        return "auth_failed"
    if status_code == 404:
        return "not_found"
    if status_code == 429:
        return "rate_limited"
    if status_code >= 500:
        return "server_error"
    return f"http_{status_code}"


async def run_tool(
    tool_name: str,
    action: str,
    ctx: Any,
    dispatch: Callable[[], Awaitable[Any]],
) -> Any:
    if trace is None:
        return await dispatch()

    try:
        meta = _get_meta(ctx)
        parent_ctx = _extract_trace_context(meta)
        tracer = trace.get_tracer("sv-mcp")
        span_cm = tracer.start_as_current_span(
            f"tools/call {tool_name}",
            context=parent_ctx,
            kind=trace.SpanKind.SERVER,
            record_exception=False,
            set_status_on_exception=False,
        )
    except Exception:
        return await dispatch()

    with span_cm as span:
        try:
            span.set_attribute("mcp.method.name", "tools/call")
            span.set_attribute("gen_ai.tool.name", tool_name)
            span.set_attribute("gen_ai.operation.name", "execute_tool")
            span.set_attribute("mcp.tool.action", action)
            client_name, client_version = _get_client_info(ctx)
            if client_name:
                span.set_attribute("mcp.client.name", client_name)
            if client_version:
                span.set_attribute("mcp.client.version", client_version)
        except Exception:
            pass

        try:
            result = await dispatch()
        except httpx.TimeoutException:
            _record_span_error(span, "timeout")
            raise
        except httpx.HTTPStatusError as e:
            _record_span_error(span, _http_status_to_error_type(e.response.status_code))
            raise
        except Exception:
            _record_span_error(span, "tool_error")
            raise

        if result is not None and getattr(result, "error", None):
            _record_span_error(span, "api_error")
        return result
