import pytest
from unittest.mock import MagicMock, patch

from sv_mcp.formatters.action import format_actions
from sv_mcp.models.result import BaseResult
from sv_mcp.models.vs.web_action import WebAction
from sv_mcp.tools.vs.action_manager import ActionManager

pytestmark = pytest.mark.asyncio

CONDITIONS = [{"matcher": {"key": "${request.query.id}", "matcherName": "equals", "matchingValue": "42"}}]
STATE_UPDATE = {
    "model": "orders",
    "filters": [],
    "parameters": [{"key": "id", "value": "${jsonPath request.body '$.id'}"}],
    "objectAction": "STORE_OBJECT",
}
WEB_ACTION = {"urlValue": "https://hooks.example.com/notify", "urlMethod": "POST", "bodyContent": None}


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


async def test_create_http_call_omits_conditions_when_not_provided(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create_http_call("call", 1, 2, WEB_ACTION)
    assert "conditions" not in mock_req.call_args.kwargs["json"]


async def test_create_http_call_passes_conditions_when_provided(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create_http_call("call", 1, 2, WEB_ACTION, conditions=CONDITIONS)
    assert mock_req.call_args.kwargs["json"]["conditions"] == CONDITIONS


async def test_create_web_hook_omits_conditions_when_not_provided(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create_web_hook("hook", 1, 2, WEB_ACTION)
    assert "conditions" not in mock_req.call_args.kwargs["json"]


async def test_create_web_hook_passes_conditions_when_provided(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create_web_hook("hook", 1, 2, WEB_ACTION, conditions=CONDITIONS)
    assert mock_req.call_args.kwargs["json"]["conditions"] == CONDITIONS


async def test_create_state_update_builds_request(manager):
    definition = {**STATE_UPDATE, "unknownKey": {"n": 1}}
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create_state_update("store order", 1, 2, definition)
    assert mock_req.call_args.args[1] == "POST"
    assert mock_req.call_args.args[2] == "/workspaces/1/transactions/2/actions"
    assert mock_req.call_args.kwargs["result_formatter"] is format_actions
    assert mock_req.call_args.kwargs["json"] == {
        "name": "store order",
        "actionType": "STATE_UPDATE",
        "definition": definition,
    }


async def test_create_state_update_passes_conditions_when_provided(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create_state_update("store order", 1, 2, STATE_UPDATE, conditions=CONDITIONS)
    assert mock_req.call_args.kwargs["json"]["conditions"] == CONDITIONS


@pytest.mark.parametrize("definition", [
    {**STATE_UPDATE, "objectAction": "ADD_OBJECT"},
    {key: value for key, value in STATE_UPDATE.items() if key != "objectAction"},
    "not a dict",
])
async def test_create_state_update_rejects_invalid_object_action_without_calling_api(manager, definition):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        result = await manager.create_state_update("store order", 1, 2, definition)
    mock_req.assert_not_called()
    assert result.error
    if isinstance(definition, dict):
        assert "STORE_OBJECT" in result.error and "INCREMENT_VALUE" in result.error


UPDATE_OBJECT = {
    "model": "orders",
    "filters": [
        {"key": "id", "operation": "EQUALS", "values": ["${request.query.id}"]},
        {"key": "status", "operation": "IN_LIST", "values": ["new", "paid"]},
    ],
    "parameters": [{"key": "status", "value": "shipped"}],
    "objectAction": "UPDATE_OBJECT",
}


async def test_create_state_update_accepts_valid_filters(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        result = await manager.create_state_update("ship order", 1, 2, UPDATE_OBJECT)
    assert result.error is None
    assert mock_req.call_args.kwargs["json"]["definition"] == UPDATE_OBJECT


@pytest.mark.parametrize("filters, message", [
    ("id=1", "filters must be a list"),
    ([{"operation": "EQUALS", "values": ["1"]}], "filters[0] must be an object with a string \"key\""),
    ([{"key": "id", "operator": "EQUALS", "values": ["1"]}], "Invalid filters[0].operation None"),
    ([{"key": "id", "operation": "NOT_EQUAL", "values": ["1"]}], "Invalid filters[0].operation 'NOT_EQUAL'"),
    ([{"key": "id", "operation": "EQUALS", "values": "1"}], "filters[0].values must be a non-empty list of strings"),
    ([{"key": "id", "operation": "EQUALS", "values": []}], "filters[0].values must be a non-empty list of strings"),
    ([{"key": "id", "operation": "EQUALS", "values": [1]}], "filters[0].values must be a non-empty list of strings"),
])
async def test_create_state_update_rejects_invalid_filters_without_calling_api(manager, filters, message):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        result = await manager.create_state_update("ship order", 1, 2, {**UPDATE_OBJECT, "filters": filters})
    mock_req.assert_not_called()
    assert message in result.error


async def test_update_rejects_invalid_object_action_without_calling_api(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        result = await manager.update(1, 2, 3, definition={**STATE_UPDATE, "objectAction": "BOGUS"})
    mock_req.assert_not_called()
    assert "Invalid objectAction 'BOGUS'" in result.error


async def test_update_with_nothing_to_change_is_rejected(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        result = await manager.update(workspace_id=1, transaction_id=2, action_id=3)
    mock_req.assert_not_called()
    assert result.error.startswith("Nothing to update")


async def test_update_checks_state_update_definition_without_object_action(manager):
    definition = {"model": "orders", "filters": [{"key": "id", "operator": "EQUALS", "values": ["1"]}]}
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        result = await manager.update(1, 2, 3, definition=definition)
    mock_req.assert_not_called()
    assert "Invalid objectAction None" in result.error


async def test_update_rejects_invalid_filters_without_calling_api(manager):
    definition = {**UPDATE_OBJECT, "filters": [{"key": "id", "operator": "EQUALS", "values": ["1"]}]}
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        result = await manager.update(1, 2, 3, definition=definition)
    mock_req.assert_not_called()
    assert "Invalid filters[0].operation None" in result.error


async def test_state_update_accepts_null_filters(manager):
    definition = {"model": "", "filters": None, "parameters": [{"key": "n", "value": "1"}],
                  "objectAction": "INCREMENT_VALUE"}
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        result = await manager.update(1, 2, 3, definition=definition)
    assert result.error is None


@pytest.mark.parametrize("parameters, message", [
    ("x", "parameters must be a list"),
    ([{"name": "id", "value": "1"}], "parameters[0] must be an object with a string \"key\""),
    ([{"key": "id"}], "parameters[0] must be an object with a string \"key\" and a \"value\""),
])
async def test_create_state_update_rejects_invalid_parameters_without_calling_api(manager, parameters, message):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        result = await manager.create_state_update("store", 1, 2, {**STATE_UPDATE, "parameters": parameters})
    mock_req.assert_not_called()
    assert message in result.error


@pytest.mark.parametrize("action_ids", [5, [], ["a"]])
async def test_reorder_rejects_invalid_action_ids(manager, action_ids):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        result = await manager.reorder(1, 2, action_ids)
    mock_req.assert_not_called()
    assert result.error == "action_ids must be a non-empty list of action ids."


async def test_update_sends_provided_fields(manager):
    definition = {"anyKey": "any value"}
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.update(1, 2, 3, action_name="renamed", definition=definition, conditions=CONDITIONS)
    assert mock_req.call_args.kwargs["json"] == {
        "id": 3,
        "name": "renamed",
        "definition": definition,
        "conditions": CONDITIONS,
    }


async def test_update_sends_empty_conditions_to_clear_them(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.update(1, 2, 3, conditions=[])
    assert mock_req.call_args.kwargs["json"] == {"id": 3, "conditions": []}


async def test_update_dumps_web_action_definition(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.update(1, 2, 3, definition=WebAction(**WEB_ACTION))
    sent = mock_req.call_args.kwargs["json"]["definition"]
    assert isinstance(sent, dict)
    assert sent["urlValue"] == "https://hooks.example.com/notify"
    assert sent["urlMethod"] == "POST"


async def test_delete_returns_info_on_success(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=["Action deleted"], total=1)
        result = await manager.delete(workspace_id=1, transaction_id=2, action_id=3)
    assert mock_req.call_args.args[1] == "DELETE"
    assert mock_req.call_args.args[2] == "/workspaces/1/transactions/2/actions/3"
    assert "result_formatter" not in mock_req.call_args.kwargs
    assert result.error is None
    assert result.info == ["Action 3 deleted"]


async def test_delete_passes_error_through(manager):
    error = BaseResult(error="Not found")
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = error
        result = await manager.delete(workspace_id=1, transaction_id=2, action_id=3)
    assert result is error


async def test_reorder_assigns_priorities_in_order(manager):
    with patch("sv_mcp.tools.vs.action_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.reorder(workspace_id=1, transaction_id=2, action_ids=[30, 10, 20])
    assert mock_req.call_args.args[1] == "POST"
    assert mock_req.call_args.args[2] == "/workspaces/1/transactions/2/actions/sort"
    assert mock_req.call_args.kwargs["result_formatter"] is format_actions
    assert mock_req.call_args.kwargs["json"] == [
        {"id": 30, "priority": 1},
        {"id": 10, "priority": 2},
        {"id": 20, "priority": 3},
    ]
