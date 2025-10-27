import traceback
from typing import Optional, Dict, Any

import httpx
from mcp.server.fastmcp import Context

from vs_mcp.config.blazemeter import VS_SERVICES_ENDPOINT, WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX
from vs_mcp.config.token import BzmToken
from vs_mcp.formatters.service import format_services
from vs_mcp.models.result import BaseResult
from vs_mcp.models.vs.service import Service
from vs_mcp.tools.utils import vs_api_request


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

    async def create(self, service_name: str, workspace_id: int) -> BaseResult:
        service_body = {
            "name": service_name,
        }
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_SERVICES_ENDPOINT}",
            result_formatter=format_services,
            json=service_body
        )

def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{VS_TOOLS_PREFIX}_service",
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
        - create: Create a new service.
            args(dict): Dictionary with the following required parameters:
                service_name (str): Mandatory. The required name of the service to create.
                workspace_id (int): Mandatory. The id of the workspace to create service in.
        Service Schema:
        """ + str(Service.model_json_schema())
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
                case "create":
                    return await service_manager.create(args["service_name"], args["workspace_id"])
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
