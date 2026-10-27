import base64

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sv_mcp.models.result import BaseResult
from sv_mcp.models.vs.sandbox_request import SandboxRequest
from sv_mcp.tools.vs.sandbox_manager import SandboxManager

pytestmark = pytest.mark.asyncio


@pytest.fixture
def manager():
    return SandboxManager(token=MagicMock(), ctx=MagicMock())


def test_sandbox_request_schema_field_is_body_not_content():
    """Backend's SandboxHttpRequest (asset-catalog) has a field named 'body', not
    'content' - advertising 'content' in our schema means the LLM caller builds a
    dict the backend silently can't bind (FAIL_ON_UNKNOWN_PROPERTIES=false, so no
    error - the body field is just left null server-side)."""
    fields = SandboxRequest.model_fields
    assert "body" in fields
    assert "content" not in fields


async def test_test_request_base64_encodes_body(manager):
    """Backend base64-decodes 'body' before use - plain text must be encoded first,
    mirroring HttpTransactionManager.to_base64 / MessagingTransactionManager.to_base64."""
    with patch("sv_mcp.tools.vs.sandbox_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.test_request(
            request={"method": "POST", "path": "/x", "name": "n", "body": '{"foo": "bar"}'},
            workspace_id=1,
        )
    http_request = mock_req.call_args.kwargs["json"]["httpRequest"]
    assert base64.b64decode(http_request["body"]).decode() == '{"foo": "bar"}'


async def test_test_request_without_body_does_not_error(manager):
    """GET requests with no body must not crash encoding and must not send a body key."""
    with patch("sv_mcp.tools.vs.sandbox_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.test_request(
            request={"method": "GET", "path": "/x", "name": "n"},
            workspace_id=1,
        )
    http_request = mock_req.call_args.kwargs["json"]["httpRequest"]
    assert "body" not in http_request
    assert "content" not in http_request


async def test_test_request_rejects_body_sent_as_content(manager):
    """`content` was the old field name. The backend ignores it, so passing it through
    would silently test with no body. It also may or may not be pre-encoded (old docs
    said base64), so it cannot be safely aliased - reject it with a clear error."""
    with patch("sv_mcp.tools.vs.sandbox_manager.vs_api_request") as mock_req:
        result = await manager.test_request(
            request={"method": "POST", "path": "/x", "name": "n", "content": '{"foo": "bar"}'},
            workspace_id=1,
        )
    mock_req.assert_not_called()
    assert result.error
    assert "body" in result.error
