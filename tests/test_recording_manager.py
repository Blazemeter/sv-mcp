import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sv_mcp.models.result import BaseResult
from sv_mcp.tools.vs.recording_manager import RecordingManager

pytestmark = pytest.mark.asyncio


@pytest.fixture
def manager():
    return RecordingManager(token=MagicMock(), ctx=MagicMock())


async def test_list_recordings(manager):
    with patch("sv_mcp.tools.vs.recording_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.list_recordings(workspace_id=1)
    url = mock_req.call_args.args[2]
    assert "/workspaces/1/recordings" in url


async def test_list_recordings_with_service_mock_filter(manager):
    with patch("sv_mcp.tools.vs.recording_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.list_recordings(workspace_id=1, service_mock_id=55)
    params = mock_req.call_args.kwargs["params"]
    assert params["serviceMockId"] == 55


async def test_read_recording(manager):
    with patch("sv_mcp.tools.vs.recording_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.read_recording(workspace_id=1, recording_id=99)
    url = mock_req.call_args.args[2]
    assert "/workspaces/1/recordings/99" in url


async def test_create_recording(manager):
    with patch("sv_mcp.tools.vs.recording_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create_recording(
            workspace_id=1,
            name="rec1",
            service_id=2,
            runtime_config={"replayCount": 3},
        )
    body = mock_req.call_args.kwargs["json"]
    assert body["name"] == "rec1"
    assert body["serviceId"] == 2
    assert body["runtimeConfig"]["replayCount"] == 3


async def test_patch_recording(manager):
    with patch("sv_mcp.tools.vs.recording_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.patch_recording(workspace_id=1, recording_id=10, name="new name")
    call = mock_req.call_args
    assert call.args[1] == "PATCH"
    assert call.kwargs["json"] == {"name": "new name"}


async def test_list_messages(manager):
    with patch("sv_mcp.tools.vs.recording_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.list_messages(workspace_id=1, recording_id=5)
    url = mock_req.call_args.args[2]
    assert "/workspaces/1/recordings/5/messages" in url


async def test_create_message(manager):
    with patch("sv_mcp.tools.vs.recording_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create_message(
            workspace_id=1,
            recording_id=5,
            message_type="TEXT_MESSAGE",
            content="aGVsbG8=",
            destination="ORDER.IN",
            destination_type="QUEUE",
        )
    body = mock_req.call_args.kwargs["json"]
    assert body["messageType"] == "TEXT_MESSAGE"
    assert body["content"] == "aGVsbG8="
    assert body["destination"] == "ORDER.IN"


async def test_patch_message(manager):
    with patch("sv_mcp.tools.vs.recording_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.patch_message(workspace_id=1, recording_id=5, message_id=20, delay=100)
    call = mock_req.call_args
    assert call.args[1] == "PATCH"
    assert call.kwargs["json"] == {"delay": 100}
