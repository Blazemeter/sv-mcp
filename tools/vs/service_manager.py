import traceback
from typing import Optional, Dict, Any
import httpx
from mcp.server.fastmcp import Context

from config.blazemeter import TOOLS_PREFIX, VS_SERVICES_ENDPOINT, WORKSPACES_ENDPOINT
from config.token import BzmToken
from formatters.service import format_services
from models.result import BaseResult
from tools import bridge
from tools.utils import vs_api_request


class ServiceManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def read(self, workspace_id: int, service_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_SERVICES_ENDPOINT}/{service_id}",
            result_formatter=format_services
        )

    async def list(self, workspace_id: int, limit: int = 50, offset: int = 0) -> BaseResult:
        parameters = {
            "limit": limit,
            "skip": offset
        }

        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_SERVICES_ENDPOINT}",
            result_formatter=format_services,
            params=parameters
        )


def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{TOOLS_PREFIX}_service",
        description="""
        Operations on services. 
        Use this when a user needs to create or select a service.
        Actions:
        - read: Read a Service. Get the information of a service.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list services from.
                service_id (int): Mandatory. The id of the service to get information.
        - list: List all services. 
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list services from.
                limit (int, default=10, valid=[1 to 50]): The number of services to list.
                offset (int, default=0): Number of services to skip.
        Hints:
        - If service id and match with that the account's workspace.
    """
    )
    async def service(action: str, args: Dict[str, Any], ctx: Context) -> BaseResult:
        service_manager = ServiceManager(token, ctx)
        try:
            match action:
                case "read":
                    return await service_manager.read(args["workspace_id"], args["service_id"])
                case "list":
                    return await service_manager.list(args["workspace_id"], args.get("limit", 50),
                                                      args.get("offset", 0))
                case _:
                    return BaseResult(
                        error=f"Action {action} not found in service manager tool"
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
