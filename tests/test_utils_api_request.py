import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sv_mcp.tools.utils import vs_api_request

pytestmark = pytest.mark.asyncio


async def test_http_error_with_empty_message_still_names_the_error():
    """httpx timeouts stringify to "", which produced a bare "HTTP error: " and left
    the caller retrying blind. The error type must always be in the message."""
    with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock,
                      side_effect=httpx.ReadTimeout("")):
        result = await vs_api_request(MagicMock(), "POST", "/x")
    assert "ReadTimeout" in result.error


async def test_http_error_keeps_the_original_message():
    with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock,
                      side_effect=httpx.ConnectError("connection refused")):
        result = await vs_api_request(MagicMock(), "POST", "/x")
    assert "ConnectError" in result.error
    assert "connection refused" in result.error
