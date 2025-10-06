import traceback
from typing import Optional, Dict, Any
import httpx
from mcp.server.fastmcp import Context

from config.blazemeter import VS_LOCATIONS_ENDPOINT, WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX
from config.token import BzmToken
from formatters.location import format_locations
from models.result import BaseResult
from models.vs.location import Location
from tools.utils import vs_api_request


class LocationManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def list(self, workspace_id: int, limit: int = 50, offset: int = 0) -> BaseResult:
        parameters = {
            "limit": limit,
            "skip": offset
        }

        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_LOCATIONS_ENDPOINT}",
            result_formatter=format_locations,
            params=parameters
        )

def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{VS_TOOLS_PREFIX}_location",
        description="""
        Operations on locations. 
        Use this when a user needs to read locations information.
        Actions:
        - list: List all locations. 
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list locations from.
        Location Schema:
        """ + str(Location.model_json_schema())
    )
    async def location(action: str, args: Dict[str, Any], ctx: Context) -> BaseResult:
        location_manager = LocationManager(token, ctx)
        try:
            match action:
                case "list":
                    return await location_manager.list(args["workspace_id"])
                case _:
                    return BaseResult(
                        error=f"Action {action} not found in location manager tool"
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
