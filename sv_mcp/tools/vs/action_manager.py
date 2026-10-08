from typing import Optional, Dict, Any, List, Union

import httpx
from mcp.server.fastmcp import Context

from sv_mcp.config.blazemeter import VS_TRANSACTIONS_ENDPOINT, VS_ACTIONS_ENDPOINT, WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX
from sv_mcp.config.token import BzmToken
from sv_mcp.formatters.action import format_actions
from sv_mcp.models.result import BaseResult
from sv_mcp.models.vs.action_condition import ActionCondition
from sv_mcp.models.vs.web_action import WebAction
from sv_mcp.telemetry import run_tool
from sv_mcp.tools.utils import vs_api_request, error_result

# The API answers an invalid objectAction or filter operation with HTTP 500, so STATE_UPDATE definitions are
# checked here first.
_STATE_UPDATE_OBJECT_ACTIONS = ("STORE_OBJECT", "UPDATE_OBJECT", "DELETE_OBJECT", "UPDATE_VALUE", "INCREMENT_VALUE")
_STATE_UPDATE_FILTER_OPERATIONS = ("EQUALS", "LESS_THAN", "GREATER_THAN", "STARTS_WITH", "ENDS_WITH", "IN_LIST")
_STATE_UPDATE_KEYS = {"model", "filters", "parameters", "objectAction"}


def _invalid_state_update(definition: Any) -> Optional[BaseResult]:
    if not isinstance(definition, dict):
        return BaseResult(error="A STATE_UPDATE definition must be a JSON object.")
    object_action = definition.get("objectAction")
    if object_action not in _STATE_UPDATE_OBJECT_ACTIONS:
        return BaseResult(error=f"Invalid objectAction {object_action!r}. "
                                f"Use one of: {', '.join(_STATE_UPDATE_OBJECT_ACTIONS)}.")
    filters = definition.get("filters") or []
    if not isinstance(filters, list):
        return BaseResult(error="filters must be a list of {\"key\", \"operation\", \"values\"} objects.")
    for index, filter_entry in enumerate(filters):
        if not isinstance(filter_entry, dict) or not isinstance(filter_entry.get("key"), str):
            return BaseResult(error=f"filters[{index}] must be an object with a string \"key\" (the data parameter name).")
        if filter_entry.get("operation") not in _STATE_UPDATE_FILTER_OPERATIONS:
            return BaseResult(error=f"Invalid filters[{index}].operation {filter_entry.get('operation')!r}. "
                                    f"Use one of: {', '.join(_STATE_UPDATE_FILTER_OPERATIONS)}.")
        values = filter_entry.get("values")
        if not isinstance(values, list) or not values or not all(isinstance(value, str) for value in values):
            return BaseResult(error=f"filters[{index}].values must be a non-empty list of strings, e.g. [\"42\"].")
    parameters = definition.get("parameters") or []
    if not isinstance(parameters, list):
        return BaseResult(error="parameters must be a list of {\"key\", \"value\"} objects.")
    for index, parameter in enumerate(parameters):
        if not isinstance(parameter, dict) or not isinstance(parameter.get("key"), str) or "value" not in parameter:
            return BaseResult(error=f"parameters[{index}] must be an object with a string \"key\" and a \"value\".")
    return None


class ActionManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def read(self, workspace_id: int, transaction_id: int, action_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{transaction_id}/{VS_ACTIONS_ENDPOINT}/{action_id}",
            result_formatter=format_actions
        )

    async def list(self, workspace_id: int, transaction_id: int, sort: Optional[str] = None) -> BaseResult:
        parameters = {}
        if sort is not None:
            parameters["sort"] = sort
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{transaction_id}/{VS_ACTIONS_ENDPOINT}",
            result_formatter=format_actions,
            params=parameters
        )

    async def create_http_call(self, action_name: str, workspace_id: int, transaction_id: int,
                               action: WebAction, conditions: Optional[List[dict]] = None) -> BaseResult:
        action_dict = action.model_dump() if isinstance(action, WebAction) else action
        action_body = {
            "name": action_name,
            "actionType": "HTTP_CALL",
            "definition": action_dict
        }
        if conditions is not None:
            action_body["conditions"] = conditions
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{transaction_id}/{VS_ACTIONS_ENDPOINT}",
            result_formatter=format_actions,
            json=action_body
        )

    async def create_web_hook(self, action_name: str, workspace_id: int, transaction_id: int,
                              action: WebAction, conditions: Optional[List[dict]] = None) -> BaseResult:
        action_dict = action.model_dump() if isinstance(action, WebAction) else action
        action_body = {
            "name": action_name,
            "actionType": "WEBHOOK",
            "definition": action_dict
        }
        if conditions is not None:
            action_body["conditions"] = conditions
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{transaction_id}/{VS_ACTIONS_ENDPOINT}",
            result_formatter=format_actions,
            json=action_body
        )

    async def create_state_update(self, action_name: str, workspace_id: int, transaction_id: int,
                                  definition: dict, conditions: Optional[List[dict]] = None) -> BaseResult:
        invalid = _invalid_state_update(definition)
        if invalid:
            return invalid
        action_body = {
            "name": action_name,
            "actionType": "STATE_UPDATE",
            "definition": definition
        }
        if conditions is not None:
            action_body["conditions"] = conditions
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{transaction_id}/{VS_ACTIONS_ENDPOINT}",
            result_formatter=format_actions,
            json=action_body
        )

    async def update(self, workspace_id: int, transaction_id: int, action_id: int,
                     action_name: Optional[str] = None, definition: Optional[Union[WebAction, dict]] = None,
                     conditions: Optional[List[dict]] = None) -> BaseResult:
        if action_name is None and definition is None and conditions is None:
            return BaseResult(error="Nothing to update. Provide at least one of action_name, definition or conditions.")
        if isinstance(definition, dict) and _STATE_UPDATE_KEYS & definition.keys():
            invalid = _invalid_state_update(definition)
            if invalid:
                return invalid
        action_body: Dict[str, Any] = {"id": action_id}
        if action_name is not None:
            action_body["name"] = action_name
        if definition is not None:
            action_body["definition"] = definition.model_dump() if isinstance(definition, WebAction) else definition
        if conditions is not None:
            action_body["conditions"] = conditions
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{transaction_id}/{VS_ACTIONS_ENDPOINT}/{action_id}",
            result_formatter=format_actions,
            json=action_body
        )

    async def delete(self, workspace_id: int, transaction_id: int, action_id: int) -> BaseResult:
        result = await vs_api_request(
            self.token,
            "DELETE",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{transaction_id}/{VS_ACTIONS_ENDPOINT}/{action_id}"
        )
        if result.error:
            return result
        return BaseResult(info=[f"Action {action_id} deleted"])

    async def reorder(self, workspace_id: int, transaction_id: int, action_ids: List[int]) -> BaseResult:
        if not isinstance(action_ids, list) or not action_ids or not all(isinstance(i, int) for i in action_ids):
            return BaseResult(error="action_ids must be a non-empty list of action ids.")
        order_body = [{"id": action_id, "priority": priority}
                      for priority, action_id in enumerate(action_ids, start=1)]
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{transaction_id}/{VS_ACTIONS_ENDPOINT}/sort",
            result_formatter=format_actions,
            json=order_body
        )

    async def assign_asset(self, id: int, transaction_id: int, workspace_id: int, type: str, assetId: int,
                           alias: str) -> BaseResult:
        assert_type_body = {
            "assetId": assetId,
            "usageType": type,
            "alias": alias
        }
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{transaction_id}/{VS_ACTIONS_ENDPOINT}/{id}/assign-asset",
            result_formatter=format_actions,
            json=assert_type_body
        )


def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{VS_TOOLS_PREFIX}_action",
        description="""
        Operations on processing actions of a transaction: HTTP calls, web hooks and state updates.
        Use this when a user needs to create, read, list, update, delete or reorder actions for a transaction,
        or to make a virtual service stateful (see "Stateful virtual services (STATE_UPDATE)" below).
        Actions:
        - read: Reads a single action of a transaction with full details.
            args(dict):
                workspace_id (int): Mandatory. The id of the workspace.
                transaction_id (int): Mandatory. The id of the transaction.
                action_id (int): Mandatory. The id of the action to read.
        - list: Lists all actions of a transaction (minimal info).
            args(dict):
                workspace_id (int): Mandatory. The id of the workspace.
                transaction_id (int): Mandatory. The id of the transaction.
                sort (str): Optional. Field to sort the actions by.
        - create_http_call: Creates an http call action for transaction. This action is executed synchronously.
            args(dict): Dictionary with the following required parameters:
                action_name (str): Mandatory. The name of the action.
                workspace_id (int): Mandatory. The id of the workspace to list services from.
                transaction_id (int): Mandatory. The id of the transaction.
                action (WebAction): Mandatory. The action definition. See WebAction schema below.
                conditions (list[ActionCondition]): Optional. Conditions that must all be true for the action to run.
                    See ActionCondition schema below.
        - create_web_hook: Creates a web hook action for transaction. This action is executed asynchronously.
            args(dict): Dictionary with the following required parameters:
                action_name (str): Mandatory. The name of the action.
                workspace_id (int): Mandatory. The id of the workspace to list services from.
                transaction_id (int): Mandatory. The id of the transaction.
                action (WebAction): Mandatory. The action definition. See WebAction schema below.
                conditions (list[ActionCondition]): Optional. Conditions that must all be true for the action to run.
                    See ActionCondition schema below.
        - create_state_update: Creates a STATE_UPDATE action that changes the virtual service's service data
            each time the transaction matches. Read "Stateful virtual services (STATE_UPDATE)" below first.
            args(dict):
                action_name (str): Mandatory. The name of the action.
                workspace_id (int): Mandatory. The id of the workspace.
                transaction_id (int): Mandatory. The id of the transaction.
                definition (dict): Mandatory. The state update definition. See "Definition shape" below.
                conditions (list[ActionCondition]): Optional. Conditions that must all be true for the action to run.
                    See ActionCondition schema below.
        - update: Updates an action of any type. Only the provided fields are changed.
            args(dict):
                workspace_id (int): Mandatory. The id of the workspace.
                transaction_id (int): Mandatory. The id of the transaction.
                action_id (int): Mandatory. The id of the action to update.
                action_name (str): Optional. The new name of the action.
                definition (WebAction | dict): Optional. The complete new definition: a WebAction for HTTP_CALL
                    and WEBHOOK actions, the state update dict for STATE_UPDATE actions. Read the action first
                    and change its current definition.
                conditions (list[ActionCondition]): Optional. The new conditions of the action.
        - delete: Deletes an action.
            args(dict):
                workspace_id (int): Mandatory. The id of the workspace.
                transaction_id (int): Mandatory. The id of the transaction.
                action_id (int): Mandatory. The id of the action to delete.
        - reorder: Sets the order in which the actions of a transaction run.
            args(dict):
                workspace_id (int): Mandatory. The id of the workspace.
                transaction_id (int): Mandatory. The id of the transaction.
                action_ids (list[int]): Mandatory. The ids of the transaction's actions in execution order;
                    the first entry runs first.
        - assign_keystore: Assign keystore asset to the action.
            args(dict):
                id (int): Mandatory. The id of the action.
                transaction_id (int): Mandatory. The id of the transaction.
                asset_id (int): Mandatory. The id of the keystore asset to assign.
                alias (str): Mandatory. The certificate alias to use.
                workspace_id (int): Mandatory. The id of the workspace.  
        - assign_certificate: Assign certificate asset to the action.
            args(dict):
                id (int): Mandatory. The id of the action.
                transaction_id (int): Mandatory. The id of the transaction.
                asset_id (int): Mandatory. The id of the certificate asset to assign.
                workspace_id (int): Mandatory. The id of the workspace.                      
        Stateful virtual services (STATE_UPDATE):
            - What it does: a STATE_UPDATE action runs after the request matches and before the response is sent.
              It modifies the virtual service's own copy of the service data. The state is shared by all clients
              and persists across stop/start. Reset it with virtual_services_state reset.
            - Prerequisites: the service must have service data (virtual_services_test_data) that defines the
              target entity or global variable. Data parameter names contain only letters, digits and
              underscores, and cannot start with a digit.
            - Read the state back in a transaction response with ${#each (blazeData 'entity' 'where ...')},
              ${blazeDataSize 'entity'} or ${globalName}.
            - Definition shape:
                {"model": "", "filters": [], "parameters": [{"key": "<name>", "value": "<value>"}],
                 "objectAction": "UPDATE_VALUE"}
                objectAction is one of STORE_OBJECT, UPDATE_OBJECT, DELETE_OBJECT, UPDATE_VALUE, INCREMENT_VALUE.
                * Global variable: model is "", filters is [], objectAction is UPDATE_VALUE (set each key to its
                  value) or INCREMENT_VALUE (add value as the step; a negative step decrements). One action can
                  change several variables.
                  A value can be a template, e.g. "${math dogFood '-' quantity}".
                * Store object (add a row): model is the entity name, filters is [], and parameters has one entry per field,
                  e.g. [{"key": "id", "value": "${jsonPath request.body '$.id'}"}]. Each match adds one row.
                * Update object / Delete object: model is the entity name, and filters selects the rows:
                  [{"key": "<data parameter>", "operation": "EQUALS", "values": ["<value>"]}]
                  operation is one of EQUALS, LESS_THAN, GREATER_THAN, STARTS_WITH, ENDS_WITH, IN_LIST.
                  values is a list of strings: one entry for most operations, one entry per item for IN_LIST.
                  A value can be a template, e.g. "${request.query.id}". LESS_THAN and GREATER_THAN compare
                  numbers. Several filters must all match. Update object sets the parameters in every matched row;
                  Delete object removes every matched row and takes parameters [].
              If the API rejects a definition, read its error, fix the definition and retry.
            - Per-key state (state keyed by a value in the request, e.g. per user, device or order id):
              1. Seed one row per key, e.g. virtual_services_test_data create_from_csv with columns account_id, locked.
              2. Read transaction: URL equals_url "/v1/accounts/${account_id}/status". The matcher selects the
                 row whose account_id is in the path, and the response reads that row, e.g. ${locked}.
              3. Write transaction: the same URL with POST and an UPDATE_OBJECT action:
                 {"model": "accounts_csv",
                  "filters": [{"key": "account_id", "operation": "EQUALS", "values": ["${account_id}"]}],
                  "parameters": [{"key": "locked", "value": "${jsonPath request.body '$.locked'}"}],
                  "objectAction": "UPDATE_OBJECT"}
                 ${account_id} in the filter value resolves to the matched row's value, so only that row changes.
              Use STORE_OBJECT with blazeData reads instead when the rows are created at runtime.
            - Verify: deploy the virtual service, send requests to it, and inspect the state with
              virtual_services_state (export_data, read_data).
            - Chaining: actions run in the order set by reorder. An HTTP call result
              ${httpcalls.<name>.response.body} can feed a later state update. conditions gate an action, and all
              of them must be true.
        WebAction Schema:
        """ + str(WebAction.model_json_schema()) + """
        ActionCondition Schema:
        """ + str(ActionCondition.model_json_schema())
    )
    async def service(action: str, args: Dict[str, Any], ctx: Context) -> BaseResult:
        action_manager = ActionManager(token, ctx)

        async def _dispatch():
            match action:
                case "read":
                    return await action_manager.read(
                        args["workspace_id"], args["transaction_id"], args["action_id"],
                    )
                case "list":
                    return await action_manager.list(
                        args["workspace_id"], args["transaction_id"], args.get("sort"),
                    )
                case "create_http_call":
                    return await action_manager.create_http_call(
                        args["action_name"], args["workspace_id"],
                        args["transaction_id"], args["action"], args.get("conditions"),
                    )
                case "create_web_hook":
                    return await action_manager.create_web_hook(
                        args["action_name"], args["workspace_id"],
                        args["transaction_id"], args["action"], args.get("conditions"),
                    )
                case "create_state_update":
                    return await action_manager.create_state_update(
                        args["action_name"], args["workspace_id"],
                        args["transaction_id"], args["definition"], args.get("conditions"),
                    )
                case "update":
                    return await action_manager.update(
                        args["workspace_id"], args["transaction_id"], args["action_id"],
                        args.get("action_name"), args.get("definition"), args.get("conditions"),
                    )
                case "delete":
                    return await action_manager.delete(
                        args["workspace_id"], args["transaction_id"], args["action_id"],
                    )
                case "reorder":
                    return await action_manager.reorder(
                        args["workspace_id"], args["transaction_id"], args["action_ids"],
                    )
                case "assign_keystore":
                    return await action_manager.assign_asset(
                        args["id"], args["transaction_id"], args["workspace_id"],
                        "CLIENT_KEYSTORE_TRUSTSTORE", args["asset_id"], args["alias"],
                    )
                case "assign_certificate":
                    return await action_manager.assign_asset(
                        args["id"], args["transaction_id"], args["workspace_id"],
                        "CLIENT_TRUSTSTORE_CERT", args["asset_id"], None,
                    )
                case _:
                    return BaseResult(error=f"Action {action} not found in action manager tool")

        try:
            return await run_tool("virtual_services_action", action, ctx, _dispatch)
        except Exception as exc:
            return error_result(exc)
