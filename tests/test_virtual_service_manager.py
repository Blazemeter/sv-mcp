import pytest
from unittest.mock import MagicMock, patch

from sv_mcp.models.result import BaseResult
from sv_mcp.tools.vs.virtual_service_manager import VirtualServiceManager

pytestmark = pytest.mark.asyncio


@pytest.fixture
def manager():
    return VirtualServiceManager(token=MagicMock(), ctx=MagicMock())


async def test_configure_without_keep_blaze_data_sends_no_params(manager):
    with patch("sv_mcp.tools.vs.base_virtual_service_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.configure(workspace_id=1, vs_id=55)
    call = mock_req.call_args
    assert call.args[1] == "GET"
    assert call.args[2] == "/workspaces/1/service-mocks/55/configure"
    assert call.kwargs["params"] == {}


async def test_configure_with_keep_blaze_data(manager):
    with patch("sv_mcp.tools.vs.base_virtual_service_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.configure(workspace_id=1, vs_id=55, keep_blaze_data=True)
    call = mock_req.call_args
    assert call.args[2] == "/workspaces/1/service-mocks/55/configure"
    assert call.kwargs["params"] == {"keepBlazeData": True}
