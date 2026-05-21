import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from sv_mcp.models.result import BaseResult
from sv_mcp.telemetry import run_tool, init_telemetry


def _make_ctx(meta=None):
    ctx = MagicMock()
    ctx.request_context.request.params.meta = meta or {}
    return ctx


def _make_tracer_and_span():
    span = MagicMock()
    cm = MagicMock()
    cm.__enter__ = MagicMock(return_value=span)
    cm.__exit__ = MagicMock(return_value=False)
    tracer = MagicMock()
    tracer.start_as_current_span.return_value = cm
    return tracer, span


class TestRunTool:
    async def test_returns_dispatch_result(self):
        ctx = _make_ctx()
        tracer, _ = _make_tracer_and_span()
        with patch("sv_mcp.telemetry.trace") as t:
            t.get_tracer.return_value = tracer
            result = BaseResult(result={"id": 1})
            returned = await run_tool("blazemeter_user", "read", ctx, AsyncMock(return_value=result))
        assert returned is result

    async def test_sets_span_attributes(self):
        ctx = _make_ctx()
        tracer, span = _make_tracer_and_span()
        with patch("sv_mcp.telemetry.trace") as t:
            t.get_tracer.return_value = tracer
            await run_tool("blazemeter_user", "read", ctx, AsyncMock(return_value=BaseResult()))
        span.set_attribute.assert_any_call("gen_ai.tool.name", "blazemeter_user")
        span.set_attribute.assert_any_call("mcp.tool.action", "read")
        span.set_attribute.assert_any_call("mcp.method.name", "tools/call")
        span.set_attribute.assert_any_call("gen_ai.operation.name", "execute_tool")

    async def test_span_kind_server(self):
        ctx = _make_ctx()
        tracer, _ = _make_tracer_and_span()
        with patch("sv_mcp.telemetry.trace") as t:
            t.get_tracer.return_value = tracer
            await run_tool("blazemeter_user", "read", ctx, AsyncMock(return_value=BaseResult()))
        _, kwargs = tracer.start_as_current_span.call_args
        assert kwargs.get("kind") == t.SpanKind.SERVER

    async def test_reraises_httpx_401(self):
        ctx = _make_ctx()
        tracer, span = _make_tracer_and_span()
        response = MagicMock()
        response.status_code = 401
        err = httpx.HTTPStatusError("unauthorized", request=MagicMock(), response=response)
        with patch("sv_mcp.telemetry.trace") as t:
            t.get_tracer.return_value = tracer
            with pytest.raises(httpx.HTTPStatusError):
                await run_tool("t", "a", ctx, AsyncMock(side_effect=err))
        span.set_attribute.assert_any_call("error.type", "auth_failed")

    async def test_reraises_httpx_404(self):
        ctx = _make_ctx()
        tracer, span = _make_tracer_and_span()
        response = MagicMock()
        response.status_code = 404
        err = httpx.HTTPStatusError("not found", request=MagicMock(), response=response)
        with patch("sv_mcp.telemetry.trace") as t:
            t.get_tracer.return_value = tracer
            with pytest.raises(httpx.HTTPStatusError):
                await run_tool("t", "a", ctx, AsyncMock(side_effect=err))
        span.set_attribute.assert_any_call("error.type", "not_found")

    async def test_reraises_httpx_500(self):
        ctx = _make_ctx()
        tracer, span = _make_tracer_and_span()
        response = MagicMock()
        response.status_code = 500
        err = httpx.HTTPStatusError("server error", request=MagicMock(), response=response)
        with patch("sv_mcp.telemetry.trace") as t:
            t.get_tracer.return_value = tracer
            with pytest.raises(httpx.HTTPStatusError):
                await run_tool("t", "a", ctx, AsyncMock(side_effect=err))
        span.set_attribute.assert_any_call("error.type", "server_error")

    async def test_reraises_httpx_timeout(self):
        ctx = _make_ctx()
        tracer, span = _make_tracer_and_span()
        err = httpx.TimeoutException("timed out")
        with patch("sv_mcp.telemetry.trace") as t:
            t.get_tracer.return_value = tracer
            with pytest.raises(httpx.TimeoutException):
                await run_tool("t", "a", ctx, AsyncMock(side_effect=err))
        span.set_attribute.assert_any_call("error.type", "timeout")

    async def test_reraises_generic_exception(self):
        ctx = _make_ctx()
        tracer, span = _make_tracer_and_span()
        with patch("sv_mcp.telemetry.trace") as t:
            t.get_tracer.return_value = tracer
            with pytest.raises(ValueError):
                await run_tool("t", "a", ctx, AsyncMock(side_effect=ValueError("boom")))
        span.set_attribute.assert_any_call("error.type", "tool_error")

    async def test_marks_span_failed_on_result_error(self):
        ctx = _make_ctx()
        tracer, span = _make_tracer_and_span()
        with patch("sv_mcp.telemetry.trace") as t:
            t.get_tracer.return_value = tracer
            result = BaseResult(error="api returned error")
            returned = await run_tool("t", "a", ctx, AsyncMock(return_value=result))
        assert returned is result
        span.set_attribute.assert_any_call("error.type", "api_error")

    async def test_survives_span_setup_failure(self):
        ctx = _make_ctx()
        with patch("sv_mcp.telemetry.trace") as t:
            t.get_tracer.side_effect = RuntimeError("otel broken")
            result = BaseResult(result={"id": 1})
            returned = await run_tool("t", "a", ctx, AsyncMock(return_value=result))
        assert returned is result

    async def test_survives_broken_ctx(self):
        ctx = MagicMock()
        ctx.request_context.request.params.meta = None
        tracer, _ = _make_tracer_and_span()
        with patch("sv_mcp.telemetry.trace") as t:
            t.get_tracer.return_value = tracer
            result = BaseResult(result={})
            returned = await run_tool("t", "a", ctx, AsyncMock(return_value=result))
        assert returned is result


class TestInitTelemetry:
    def test_does_not_raise_without_sdk(self):
        init_telemetry("sv-mcp", "1.0.0")

    def test_does_not_raise_with_disabled_flag(self, monkeypatch):
        monkeypatch.setenv("OTEL_SDK_DISABLED", "true")
        init_telemetry("sv-mcp", "1.0.0")

    def test_does_not_raise_with_endpoint_set(self, monkeypatch):
        monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
        init_telemetry("sv-mcp", "1.0.0")
