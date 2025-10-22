import traceback
from typing import Optional, Dict, Any

import httpx
from mcp.server.fastmcp import Context

from config.blazemeter import VS_SANDBOX_ENDPOINT, VS_TOOLS_PREFIX, WORKSPACES_ENDPOINT
from config.token import BzmToken
from formatters.sandbox import format_sandbox_test_request, format_sandbox
from models.result import BaseResult
from models.vs.sandbox_request import SandboxRequest
from models.vs.sandbox_response import SandboxResponse
from tools.utils import vs_api_request


class SandboxManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def init(self, workspace_id: int, transaction_id: int) -> BaseResult:
        parameters = {
            "transactionId": transaction_id
        }
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_SANDBOX_ENDPOINT}",
            result_formatter=format_sandbox,
            params=parameters
        )

    async def test_request(self, request: SandboxRequest, workspace_id: int) -> BaseResult:
        sandbox_request = {
            "httpRequest": request,
        }
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_SANDBOX_ENDPOINT}/test-request",
            result_formatter=format_sandbox_test_request,
            json=sandbox_request
        )


def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{VS_TOOLS_PREFIX}_sandbox",
        description="""
        Testing HTTP transactions in sandbox. 
        Use this for HTTP transaction verification.
        MESSAGING transactions are not supported in sandbox.
        Actions:
        - init: Places transaction into sandbox.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace.
                transaction_id (int): Mandatory. The id of the transaction to test.
        - test_request: Sends test request to sandbox. 
            args(dict): Dictionary with the following required parameters:
                request (SandboxRequest): Mandatory. The request definition.
                workspace_id (int): Mandatory. The id of the workspace.
        Sandbox Request Schema:
        """ + str(SandboxRequest.model_json_schema()) + """
        Sandbox test_request response schema:
        """ + str(SandboxResponse.model_json_schema())
    )
    async def sandbox(action: str, args: Dict[str, Any], ctx: Context) -> BaseResult:
        sandbox_manager = SandboxManager(token, ctx)
        try:
            match action:
                case "init":
                    return await sandbox_manager.init(args["workspace_id"], args["transaction_id"])
                case "test_request":
                    return await sandbox_manager.test_request(
                        args["request"],
                        args["workspace_id"]
                    )
                case _:
                    return BaseResult(
                        error=f"Action {action} not found in sandbox manager tool"
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
