"""
Simple utilities for BlazeMeter MCP tools.
"""
import os
import platform
from datetime import datetime
from typing import Optional, Callable

import httpx

from vs_mcp.config.blazemeter import BZM_API_BASE_URL, VS_API_BASE_URL
from vs_mcp.config.token import BzmToken
from vs_mcp.config.version import __version__
from vs_mcp.models.result import BaseResult

# Collect system info once
ua_part = f"{platform.system()} {platform.release()}; {platform.machine()}"

def _build_headers(token: BzmToken, extra_headers: Optional[dict] = None) -> dict:
    headers = extra_headers or {}
    headers["Authorization"] = token.as_basic_auth()
    headers["User-Agent"] = f"bzm-mcp/{__version__} ({ua_part})"
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
            resp = await client.request(method, endpoint, headers=headers, **kwargs)
            resp.raise_for_status()
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
        except httpx.HTTPError as e:
            if e.response.status_code in (401, 403):
                return BaseResult(error="Invalid credentials")
            data = e.response.json()
            return BaseResult(error=str(data.get("error")))

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

def get_date_time_iso(timestamp: Optional[int]) -> Optional[str]:
    return datetime.fromtimestamp(timestamp).isoformat() if timestamp is not None else None
