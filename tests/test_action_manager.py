import pytest
from unittest.mock import MagicMock, patch

from sv_mcp.formatters.action import format_actions
from sv_mcp.models.result import BaseResult
from sv_mcp.tools.vs.action_manager import ActionManager

pytestmark = pytest.mark.asyncio


@pytest.fixture
def manager():
    return ActionManager(token=MagicMock(), ctx=MagicMock())


async def test_read_builds_action_endpoint(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.read(workspace_id=1, transaction_id=2, action_id=3)
    assert mock_req.call_args.args[1] == "GET"
    assert mock_req.call_args.args[2] == "/workspaces/1/transactions/2/actions/3"
    assert mock_req.call_args.kwargs["result_formatter"] is format_actions


async def test_list_builds_actions_endpoint(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.list(workspace_id=1, transaction_id=2)
    assert mock_req.call_args.args[1] == "GET"
    assert mock_req.call_args.args[2] == "/workspaces/1/transactions/2/actions"
    assert mock_req.call_args.kwargs["result_formatter"] is format_actions


async def test_list_omits_sort_when_not_provided(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.list(workspace_id=1, transaction_id=2)
    params = mock_req.call_args.kwargs.get("params") or {}
    assert "sort" not in params


async def test_list_passes_sort_when_provided(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.list(workspace_id=1, transaction_id=2, sort="name")
    assert mock_req.call_args.kwargs["params"]["sort"] == "name"
