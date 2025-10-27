import traceback
from typing import Optional, Dict, Any

import httpx
from mcp.server.fastmcp import Context

from vs_mcp.config.blazemeter import VS_CONFIGURATIONS_ENDPOINT, WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX
from vs_mcp.config.token import BzmToken
from vs_mcp.formatters.configuration import format_configurations
from vs_mcp.models.result import BaseResult
from vs_mcp.models.vs.configuration import Configuration
from vs_mcp.tools.utils import vs_api_request


class ConfigurationManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def read(self, workspace_id: int, configuration_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_CONFIGURATIONS_ENDPOINT}/{configuration_id}",
            result_formatter=format_configurations
        )

    async def list(self, workspace_id: int, limit: int = 50, offset: int = 0) -> BaseResult:
        parameters = {
            "limit": limit,
            "skip": offset
        }

        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_CONFIGURATIONS_ENDPOINT}",
            result_formatter=format_configurations,
            params=parameters
        )

    async def create(self, workspace_id: int, configuration_name: str, configuration_map: dict) -> BaseResult:
        transformed = {}
        if configuration_map:
            transformed = {k: {"type": "string", "value": v} for k, v in configuration_map.items()}
        config_body = {
            "name": configuration_name,
            "configurationMap": transformed
        }
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_CONFIGURATIONS_ENDPOINT}",
            result_formatter=format_configurations,
            json=config_body
        )

    async def update(self, workspace_id: int, configuration_id: int, configuration_name: str,
                     configuration_map: dict) -> BaseResult:
        transformed = {}
        if configuration_map:
            transformed = {k: {"type": "string", "value": v} for k, v in configuration_map.items()}
        config_body = {
            "name": configuration_name,
            "configurationMap": transformed
        }
        return await vs_api_request(
            self.token,
            "PUT",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_CONFIGURATIONS_ENDPOINT}/{configuration_id}",
            result_formatter=format_configurations,
            json=config_body
        )


def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{VS_TOOLS_PREFIX}_configuration",
        description="""
        Operations on virtual service configurations. 
        Use this when a user needs to create or update a virtual service configuration.
        Actions:
        - read: Read a Configuration.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list configurations from.
                configuration_id (int): Mandatory. The id of the configuration to get information.
        - list: List all configurations. 
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list configurations from.
                limit (int, default=10, valid=[1 to 50]): The number of configurations to list.
                offset (int, default=0): Number of configurations to skip.
        - create: Create a new configuration.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The ID of the workspace in which to create the configuration.
                configuration_name (str): Mandatory. The name of the configuration to create.
                configuration_map (Dict[str, str]): Mandatory. A map of configuration parameters and their corresponding values.
        - update: Update an existing configuration.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The ID of the workspace containing the configuration.
                configuration_id (int): Mandatory. The ID of the configuration to update.
                configuration_name (str): Mandatory. The new or updated name of the configuration.
                configuration_map (Dict[str, str]): Mandatory. A map of configuration parameters and their corresponding values.
        Configuration Schema:
        """ + str(Configuration.model_json_schema())
    )
    async def service(action: str, args: Dict[str, Any], ctx: Context) -> BaseResult:
        config_manager = ConfigurationManager(token, ctx)
        try:
            match action:
                case "read":
                    return await config_manager.read(args["workspace_id"], args["configuration_id"])
                case "list":
                    return await config_manager.list(args["workspace_id"], args.get("limit", 50),
                                                     args.get("offset", 0))
                case "create":
                    return await config_manager.create(args["workspace_id"], args["configuration_name"],
                                                       args["configuration_map"])
                case "update":
                    return await config_manager.update(args["workspace_id"], args["configuration_id"],
                                                       args["configuration_name"], args["configuration_map"])
                case _:
                    return BaseResult(
                        error=f"Action {action} not found in configuration manager tool"
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
