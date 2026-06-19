from typing import Optional, Dict, Any

import httpx
from mcp.server.fastmcp import Context

from sv_mcp.config.blazemeter import VS_SANDBOX_ENDPOINT, VS_TOOLS_PREFIX, WORKSPACES_ENDPOINT
from sv_mcp.config.token import BzmToken
from sv_mcp.formatters.sandbox import format_sandbox_test_request, format_sandbox
from sv_mcp.models.result import BaseResult
from sv_mcp.models.vs.sandbox_request import SandboxRequest
from sv_mcp.models.vs.sandbox_response import SandboxResponse
from sv_mcp.telemetry import run_tool
from sv_mcp.tools.utils import vs_api_request, error_result


class SandboxManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def init(self, workspace_id: int, transaction_id: int) -> BaseResult:
        parameters = {
            "transactionId": transaction_id
        }
        result = await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_SANDBOX_ENDPOINT}",
            result_formatter=format_sandbox,
            params=parameters
        )
        result.append_info(["Sandbox initialized. You MUST now call 'test_request' action with the HTTP request details to actually run the test."])
        return result

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
        Use this for HTTP transaction verification, or to re-test an existing transaction after update.
        MESSAGING transactions are not supported in sandbox.
        IMPORTANT: Testing a transaction in the sandbox ALWAYS requires two sequential tool calls:
          1. Call `init` first — places the transaction into the sandbox environment.
          2. Then call `test_request` — sends the actual HTTP request and returns the match result.
        Both steps are mandatory. Calling only `init` does NOT test anything; you MUST follow it with `test_request`.
        Response fields: matched=true means the request was matched by the configured transaction.
        matched=false means no transaction matched — read mismatch_reasons to understand which
        matchers failed and what to fix in the DSL.
        Actions:
        - init: Places transaction into sandbox. Must be called BEFORE test_request.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace.
                transaction_id (int): Mandatory. The id of the transaction to test.
        - test_request: Sends test request to sandbox and returns match result. Must be called AFTER init.
            args(dict): Dictionary with the following required parameters:
                request (SandboxRequest): Mandatory. The request definition (method, path, headers, body).
                workspace_id (int): Mandatory. The id of the workspace.
        Sandbox Request Schema:
        """ + str(SandboxRequest.model_json_schema()) + """
        Sandbox test_request response schema:
        """ + str(SandboxResponse.model_json_schema())
    )
    async def sandbox(action: str, args: Dict[str, Any], ctx: Context) -> BaseResult:
        sandbox_manager = SandboxManager(token, ctx)

        async def _dispatch():
            match action:
                case "init":
                    return await sandbox_manager.init(args["workspace_id"], args["transaction_id"])
                case "test_request":
                    return await sandbox_manager.test_request(args["request"], args["workspace_id"])
                case _:
                    return BaseResult(error=f"Action {action} not found in sandbox manager tool")

        try:
            return await run_tool("virtual_services_sandbox", action, ctx, _dispatch)
        except Exception as exc:
            return error_result(exc)
