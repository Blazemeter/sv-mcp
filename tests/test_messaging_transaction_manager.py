import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sv_mcp.models.result import BaseResult
from sv_mcp.tools.vs.messaging_transaction_manager import MessagingTransactionManager

pytestmark = pytest.mark.asyncio


@pytest.fixture
def manager():
    return MessagingTransactionManager(token=MagicMock(), ctx=MagicMock())


async def test_list_with_service_mock_id(manager):
    with patch("sv_mcp.tools.vs.messaging_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.list(workspace_id=1, service_id=None, service_mock_id=99)
    params = mock_req.call_args.kwargs["params"]
    assert params["serviceMockId"] == 99


async def test_list_without_service_mock_id(manager):
    with patch("sv_mcp.tools.vs.messaging_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.list(workspace_id=1, service_id=5)
    params = mock_req.call_args.kwargs["params"]
    assert "serviceMockId" not in params
    assert params["serviceId"] == 5


async def test_create_normalizes_invalid_base64_content(manager):
    """Invalid base64 in responseDsl.content is re-encoded as UTF-8 plain text."""
    with patch("sv_mcp.tools.vs.messaging_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create(
            transaction_name="t1",
            workspace_id=1,
            service_id=2,
            type="MESSAGING",
            dsl={
                "requestDsl": {"body": []},
                "responseDsl": {"content": 'eyJzdGF0dXMib2si}'},  # stray } makes it invalid
            },
            delay=None,
        )
    body = mock_req.call_args.kwargs["json"]
    content = body["transactions"][0]["dsl"]["responseDsl"]["content"]
    import base64
    decoded = base64.b64decode(content).decode('utf-8')
    assert decoded == 'eyJzdGF0dXMib2si}'


async def test_create_preserves_valid_base64_content(manager):
    """Valid base64 content is kept unchanged."""
    import base64
    valid_b64 = base64.b64encode(b'{"status":"ok"}').decode()
    with patch("sv_mcp.tools.vs.messaging_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create(
            transaction_name="t1",
            workspace_id=1,
            service_id=2,
            type="MESSAGING",
            dsl={"requestDsl": {"body": []}, "responseDsl": {"content": valid_b64}},
            delay=None,
        )
    body = mock_req.call_args.kwargs["json"]
    assert body["transactions"][0]["dsl"]["responseDsl"]["content"] == valid_b64


async def test_create_encodes_plain_text_content(manager):
    """Plain text content (non-base64) is auto-encoded to base64."""
    import base64
    with patch("sv_mcp.tools.vs.messaging_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create(
            transaction_name="t1",
            workspace_id=1,
            service_id=2,
            type="MESSAGING",
            dsl={"requestDsl": {"body": []}, "responseDsl": {"content": '{"status":"ok"}'}},
            delay=None,
        )
    body = mock_req.call_args.kwargs["json"]
    content = body["transactions"][0]["dsl"]["responseDsl"]["content"]
    assert base64.b64decode(content).decode() == '{"status":"ok"}'


async def test_create_injects_dsl_type_when_missing(manager):
    """dsl.type must be present for correct Jackson polymorphic deserialization on the API side."""
    with patch("sv_mcp.tools.vs.messaging_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create(
            transaction_name="t1",
            workspace_id=1,
            service_id=2,
            type="MESSAGING",
            dsl={"requestDsl": {"body": []}, "responseDsl": {"content": "eyJzdGF0dXMiOiAib2sifQ=="}},
            delay=None,
        )
    body = mock_req.call_args.kwargs["json"]
    assert body["transactions"][0]["dsl"]["type"] == "MESSAGING"


async def test_create_preserves_existing_dsl_type(manager):
    with patch("sv_mcp.tools.vs.messaging_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create(
            transaction_name="t1",
            workspace_id=1,
            service_id=2,
            type="MESSAGING",
            dsl={"type": "MESSAGING", "requestDsl": {"body": []}, "responseDsl": {}},
            delay=None,
        )
    body = mock_req.call_args.kwargs["json"]
    assert body["transactions"][0]["dsl"]["type"] == "MESSAGING"


async def test_update_injects_dsl_type_when_missing(manager):
    with patch("sv_mcp.tools.vs.messaging_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.update(
            id=10,
            transaction_name="t1",
            workspace_id=1,
            type="MESSAGING",
            dsl={"requestDsl": {"body": []}, "responseDsl": {}},
            delay=None,
        )
    body = mock_req.call_args.kwargs["json"]
    assert body["dsl"]["type"] == "MESSAGING"


async def test_create_with_extra_fields(manager):
    with patch("sv_mcp.tools.vs.messaging_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create(
            transaction_name="t1",
            workspace_id=1,
            service_id=2,
            type="MESSAGING",
            dsl={"type": "MESSAGING", "requestDsl": {}, "responseDsl": {}},
            delay=None,
            description="my desc",
            tags=["billing"],
            priority=5,
            messaging_transaction_mappings={"sourceName": "IN.Q", "sourceType": "QUEUE", "destinations": []},
            sample_body="hello",
        )
    body = mock_req.call_args.kwargs["json"]
    txn = body["transactions"][0]
    assert txn["description"] == "my desc"
    assert txn["tags"] == ["billing"]
    assert txn["priority"] == 5
    assert txn["messagingTransactionMappings"]["sourceName"] == "IN.Q"
    assert txn["sampleBody"] == "hello"


async def test_update_with_extra_fields(manager):
    with patch("sv_mcp.tools.vs.messaging_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.update(
            id=10,
            transaction_name="t1",
            workspace_id=1,
            type="MESSAGING",
            dsl={"type": "MESSAGING", "requestDsl": {}, "responseDsl": {}},
            delay=None,
            description="updated",
            tags=["v2"],
            priority=3,
            messaging_transaction_mappings=None,
            sample_body=None,
        )
    body = mock_req.call_args.kwargs["json"]
    assert body["description"] == "updated"
    assert body["tags"] == ["v2"]
    assert body["priority"] == 3
