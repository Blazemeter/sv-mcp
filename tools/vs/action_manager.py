import traceback
from typing import Optional, Dict, Any

import httpx
from mcp.server.fastmcp import Context

from config.blazemeter import VS_TRANSACTIONS_ENDPOINT, VS_ACTIONS_ENDPOINT, WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX
from config.token import BzmToken
from formatters.action import format_actions
from models.result import BaseResult
from models.vs.web_action import WebAction
from tools.utils import vs_api_request


class ActionManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def create_http_call(self, action_name: str, workspace_id: int, transaction_id: int,
                               action: WebAction) -> BaseResult:
        action_dict = action.model_dump() if isinstance(action, WebAction) else action
        action_body = {
            "name": action_name,
            "actionType": "HTTP_CALL",
            "definition": action_dict
        }
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{transaction_id}/{VS_ACTIONS_ENDPOINT}",
            result_formatter=format_actions,
            json=action_body
        )

    async def create_web_hook(self, action_name: str, workspace_id: int, transaction_id: int,
                              action: WebAction) -> BaseResult:
        action_dict = action.model_dump() if isinstance(action, WebAction) else action
        action_body = {
            "name": action_name,
            "actionType": "WEBHOOK",
            "definition": action_dict
        }
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{transaction_id}/{VS_ACTIONS_ENDPOINT}",
            result_formatter=format_actions,
            json=action_body
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
        Operations on actions. 
        Use this when a user needs to create an action for transaction.
        Actions:
        - create_http_call: Creates an http call action for transaction. This action is executed synchronously.
            args(dict): Dictionary with the following required parameters:
                action_name (str): Mandatory. The name of the action.
                workspace_id (int): Mandatory. The id of the workspace to list services from.
                transaction_id (int): Mandatory. The id of the transaction.
                action (WebAction): Mandatory. The action definition. See WebAction schema below.
        - create_web_hook: Creates a web hook action for transaction. This action is executed asynchronously.
            args(dict): Dictionary with the following required parameters:
                action_name (str): Mandatory. The name of the action.
                workspace_id (int): Mandatory. The id of the workspace to list services from.
                transaction_id (int): Mandatory. The id of the transaction.
                action (WebAction): Mandatory. The action definition. See WebAction schema below.
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
        Action Schema:
        """ + str(WebAction.model_json_schema())
    )
    async def service(action: str, args: Dict[str, Any], ctx: Context) -> BaseResult:
        action_manager = ActionManager(token, ctx)
        try:
            match action:
                case "create_http_call":
                    return await action_manager.create_http_call(args["action_name"], args["workspace_id"],
                                                                 args["transaction_id"], args["action"])
                case "create_web_hook":
                    return await action_manager.create_web_hook(args["action_name"], args["workspace_id"],
                                                                args["transaction_id"], args["action"])
                case "assign_keystore":
                    return await action_manager.assign_asset(
                        args["id"],
                        args["transaction_id"],
                        args["workspace_id"],
                        "CLIENT_KEYSTORE_TRUSTSTORE",
                        args["asset_id"],
                        args["alias"],
                    )
                case "assign_certificate":
                    return await action_manager.assign_asset(
                        args["id"],
                        args["transaction_id"],
                        args["workspace_id"],
                        "CLIENT_TRUSTSTORE_CERT",
                        args["asset_id"],
                        None)
                case _:
                    return BaseResult(
                        error=f"Action {action} not found in action manager tool"
                    )
        except httpx.HTTPStatusError:
            return BaseResult(
                error=f"Error: {traceback.format_exc()}"
            )
        except Exception:
            return BaseResult(
                error=f"""Error: {traceback.format_exc()}
                          If you think this is a bug, please contact BlazeMeter support or report issue at https://github.com/BlazeMeter/bzm-mcp/issues"""
            )
