from unittest.mock import MagicMock, patch

import httpx

from sv_mcp.tools.utils import vs_api_request

_RealAsyncClient = httpx.AsyncClient


def _client_returning(response: httpx.Response):
    """Patch target for httpx.AsyncClient: same client, but every request gets `response`."""
    def factory(**kwargs):
        kwargs.pop("http2", None)
        return _RealAsyncClient(transport=httpx.MockTransport(lambda request: response), **kwargs)
    return factory


def _token():
    token = MagicMock()
    token.as_basic_auth.return_value = "Basic abc"
    return token


async def test_json_envelope_result_is_unwrapped():
    response = httpx.Response(200, json={"result": [{"id": 1}], "total": 1, "skip": 0, "limit": 1})
    with patch("sv_mcp.tools.utils.httpx.AsyncClient", _client_returning(response)):
        result = await vs_api_request(_token(), "GET", "/things")
    assert result.result == [{"id": 1}]
    assert result.error is None


async def test_plain_text_body_is_returned_as_result_not_crash():
    response = httpx.Response(200, text="OK")
    with patch("sv_mcp.tools.utils.httpx.AsyncClient", _client_returning(response)):
        result = await vs_api_request(_token(), "GET", "/things/1")
    assert result.result == ["OK"]
    assert result.error is None


async def test_bare_json_string_body_is_returned_as_result_not_crash():
    response = httpx.Response(200, json="OK")
    with patch("sv_mcp.tools.utils.httpx.AsyncClient", _client_returning(response)):
        result = await vs_api_request(_token(), "GET", "/things/1")
    assert result.result == ["OK"]
    assert result.total == 1


async def test_bare_json_array_body_is_formatted_like_an_envelope_result():
    response = httpx.Response(200, json=[{"id": 1}, {"id": 2}])
    with patch("sv_mcp.tools.utils.httpx.AsyncClient", _client_returning(response)):
        result = await vs_api_request(
            _token(), "GET", "/things", result_formatter=lambda items, params: [i["id"] for i in items]
        )
    assert result.result == [1, 2]


async def test_empty_body_returns_empty_result():
    response = httpx.Response(204)
    with patch("sv_mcp.tools.utils.httpx.AsyncClient", _client_returning(response)):
        result = await vs_api_request(_token(), "DELETE", "/things/1")
    assert result.result is None
    assert result.error is None
