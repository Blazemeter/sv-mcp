"""
Simple utilities for BlazeMeter MCP tools.
"""
import logging
import os
import platform
from datetime import datetime
from typing import Optional, Callable

import httpx

from sv_mcp.config.blazemeter import BZM_API_BASE_URL, VS_API_BASE_URL, TDM_API_BASE_URL
from sv_mcp.config.token import BzmToken
from sv_mcp.config.version import __version__
from sv_mcp.models.result import BaseResult

logger = logging.getLogger(__name__)

# Collect system info once
ua_part = f"{platform.system()} {platform.release()}; {platform.machine()}"

def _build_headers(token: BzmToken, extra_headers: Optional[dict] = None) -> dict:
    headers = extra_headers or {}
    headers["Authorization"] = token.as_basic_auth()
    headers["User-Agent"] = f"sv-mcp/{__version__} ({ua_part})"
    return headers

async def _api_request(base_url: str,
                       token: Optional[BzmToken],
                       method: str,
                       endpoint: str,
                       result_formatter: Optional[Callable] = None,
                       result_formatter_params: Optional[dict] = None,
                       **kwargs) -> BaseResult:
    """
    Generalized API request for BlazeMeter/VS API with common logic.
    """
    if not token:
        return BaseResult(
            error="No API token. Set API_KEY_PATH env var with file path or API_KEY_ID and API_KEY_SECRET secrets in docker catalog configuration."
        )

    headers = _build_headers(token, kwargs.pop("headers", {}))
    timeout = httpx.Timeout(connect=15.0, read=60.0, write=15.0, pool=60.0)

    async with httpx.AsyncClient(base_url=base_url, http2=True, timeout=timeout) as client:
        try:
            if logger.isEnabledFor(logging.DEBUG):
                req_body = kwargs.get("json") or kwargs.get("data") or kwargs.get("content")
                logger.debug("→ %s %s%s  body=%s", method, base_url, endpoint, req_body)
            resp = await client.request(method, endpoint, headers=headers, **kwargs)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("← %s %s  body=%.3000s", resp.status_code, resp.url, resp.text)
            resp.raise_for_status()
            if resp.status_code == 204 or not resp.content:
                return BaseResult()
            data = resp.json()

            result = data.get("result", [])
            default_total = 0
            if not isinstance(result, list):
                result = [result]
                default_total = 1

            final_result = result_formatter(result, result_formatter_params) if result_formatter else result
            total = data.get("total", default_total)
            skip, limit = data.get("skip", 0), data.get("limit", 0)

            return BaseResult(
                result=final_result,
                error=data.get("error"),
                total=total,
                has_more=(total - (skip + limit)) > 0
            )
        except httpx.HTTPStatusError as e:
            try:
                data = e.response.json()
                server_msg = data.get("error") or data.get("message") or e.response.text
            except Exception:
                server_msg = e.response.text or str(e)
            if e.response.status_code == 401:
                return BaseResult(error=f"Invalid credentials: {server_msg}")
            if e.response.status_code == 403:
                return BaseResult(error=f"Access forbidden (check workspace permissions): {server_msg}")
            return BaseResult(error=str(server_msg) or str(e))
        except httpx.HTTPError as e:
            return BaseResult(error=f"HTTP error: {e}")

# Thin wrappers
async def bzm_api_request(token: Optional[BzmToken], method: str, endpoint: str,
                          result_formatter: Optional[Callable] = None,
                          result_formatter_params: Optional[dict] = None,
                          **kwargs) -> BaseResult:
    return await _api_request(os.getenv('BZM_URL', BZM_API_BASE_URL), token, method, endpoint,
                              result_formatter, result_formatter_params, **kwargs)

async def vs_api_request(token: Optional[BzmToken], method: str, endpoint: str,
                         result_formatter: Optional[Callable] = None,
                         result_formatter_params: Optional[dict] = None,
                         **kwargs) -> BaseResult:
    return await _api_request(os.getenv('VS_URL', VS_API_BASE_URL), token, method, endpoint,
                              result_formatter, result_formatter_params, **kwargs)

async def tdm_api_request(token: Optional[BzmToken], method: str, endpoint: str,
                          result_formatter: Optional[Callable] = None,
                          result_formatter_params: Optional[dict] = None,
                          **kwargs) -> BaseResult:
    return await _api_request(os.getenv('TDM_URL', TDM_API_BASE_URL), token, method, endpoint,
                              result_formatter, result_formatter_params, **kwargs)

def error_result(exc: Exception) -> BaseResult:
    """
    Convert an exception into a clean, classified BaseResult error.

    Distinguishes request problems (4xx), environmental problems (timeout /
    network), and system failures (5xx / unexpected) so an agent can pick a
    valid recovery path. Never returns raw tracebacks or internal server state
    to the caller — full diagnostics are logged server-side instead.
    """
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        try:
            data = exc.response.json()
            server_msg = data.get("error") or data.get("message") or ""
        except Exception:
            server_msg = ""
        if code == 401:
            return BaseResult(error=f"Invalid credentials: {server_msg}".strip())
        if code == 403:
            return BaseResult(error=f"Access forbidden (check workspace permissions): {server_msg}".strip())
        if code == 404:
            return BaseResult(error=f"Not found: {server_msg}".strip())
        if code == 429:
            return BaseResult(error=f"Rate limited by BlazeMeter; wait a moment before retrying. {server_msg}".strip())
        if code >= 500:
            return BaseResult(error=f"BlazeMeter service error (HTTP {code}); this is a server-side problem, retry later.")
        return BaseResult(error=(server_msg or f"Request failed (HTTP {code})."))
    if isinstance(exc, httpx.TimeoutException):
        return BaseResult(error="Request to BlazeMeter timed out; the service may be slow or unreachable. Retry shortly.")
    if isinstance(exc, httpx.HTTPError):
        return BaseResult(error="Network error contacting BlazeMeter; check connectivity and retry.")
    logger.exception("Unexpected error in tool dispatch")
    return BaseResult(
        error=f"Internal error: {type(exc).__name__}. "
              "If you think this is a bug, please contact BlazeMeter support or "
              "report the issue at https://github.com/BlazeMeter/bzm-mcp/issues"
    )


def get_date_time_iso(timestamp: Optional[int]) -> Optional[str]:
    return datetime.fromtimestamp(timestamp).isoformat() if timestamp is not None else None
