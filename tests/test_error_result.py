import httpx
from unittest.mock import MagicMock

from sv_mcp.tools.utils import error_result


def _http_error(status_code: int, body: dict | None = None, text: str = ""):
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    if body is not None:
        response.json.return_value = body
    else:
        response.json.side_effect = ValueError("no json")
    response.text = text
    return httpx.HTTPStatusError("err", request=MagicMock(), response=response)


class TestErrorResult:
    def test_401_is_invalid_credentials(self):
        r = error_result(_http_error(401, {"error": "bad key"}))
        assert r.error == "Invalid credentials: bad key"

    def test_403_is_access_forbidden(self):
        r = error_result(_http_error(403, {"message": "nope"}))
        assert r.error == "Access forbidden (check workspace permissions): nope"

    def test_404_is_not_found(self):
        r = error_result(_http_error(404, {"error": "missing"}))
        assert r.error == "Not found: missing"

    def test_429_is_rate_limited(self):
        r = error_result(_http_error(429))
        assert "Rate limited" in r.error

    def test_5xx_is_server_error(self):
        r = error_result(_http_error(503))
        assert "server-side problem" in r.error
        assert "503" in r.error

    def test_timeout_is_environmental(self):
        r = error_result(httpx.TimeoutException("slow"))
        assert "timed out" in r.error

    def test_network_error(self):
        r = error_result(httpx.ConnectError("refused"))
        assert "Network error" in r.error

    def test_unexpected_exception_has_no_traceback(self):
        r = error_result(ValueError("secret /home/user/path leaked"))
        # Clean, classified message — no raw value or stack trace forwarded.
        assert r.error.startswith("Internal error: ValueError")
        assert "secret" not in r.error
        assert "/home/user/path" not in r.error
        assert "Traceback" not in r.error

    def test_never_forwards_raw_traceback_for_http_errors(self):
        r = error_result(_http_error(500))
        assert "Traceback" not in r.error
