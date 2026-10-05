import pytest
from unittest.mock import MagicMock, patch

from sv_mcp.formatters.service_data import format_service_data
from sv_mcp.formatters.virtual_service import format_virtual_services_action
from sv_mcp.models.result import BaseResult
from sv_mcp.tools.vs.state_manager import StateManager

pytestmark = pytest.mark.asyncio


@pytest.fixture
def manager():
    return StateManager(token=MagicMock(), ctx=MagicMock())


async def test_read_data_builds_testdata_endpoint(manager):
    with patch("sv_mcp.tools.vs.state_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.read_data(workspace_id=1, vs_id=55)
    call = mock_req.call_args
    assert call.args[1] == "GET"
    assert call.args[2] == "/workspaces/1/service-mocks/55/testdata"
    assert call.kwargs["result_formatter"] is format_service_data


async def test_export_data_builds_refresh_endpoint(manager):
    with patch("sv_mcp.tools.vs.state_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.export_data(workspace_id=1, vs_id=55)
    call = mock_req.call_args
    assert call.args[1] == "GET"
    assert call.args[2] == "/workspaces/1/service-mocks/55/testdata/refresh"
    assert call.kwargs["result_formatter"] is format_virtual_services_action


async def test_reset_reconfigures_without_keeping_data(manager):
    # reset reuses BaseVirtualServiceManager.configure, so the request is made from that module
    with patch("sv_mcp.tools.vs.base_virtual_service_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.reset(workspace_id=1, vs_id=55)
    call = mock_req.call_args
    assert call.args[1] == "GET"
    assert call.args[2] == "/workspaces/1/service-mocks/55/configure"
    assert call.kwargs["params"] == {"keepBlazeData": False}
    assert call.kwargs["result_formatter"] is format_virtual_services_action
