import traceback
from typing import Optional, Dict, Any

import httpx
from mcp.server.fastmcp import Context

from vs_mcp.config.blazemeter import VS_TOOLS_PREFIX, VS_TRACKINGS_ENDPOINT
from vs_mcp.config.token import BzmToken
from vs_mcp.formatters.tracking import format_trackings, format_asset_trackings
from vs_mcp.models.result import BaseResult
from vs_mcp.models.vs.trackings import MasterTracking
from vs_mcp.tools.utils import vs_api_request


class TrackingManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def read(self, tracking_id: str) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"/{VS_TRACKINGS_ENDPOINT}/{tracking_id}",
            result_formatter=format_trackings
        )

    async def read_asset_tracking(self, tracking_id: str) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"/{VS_TRACKINGS_ENDPOINT}/{tracking_id}",
            result_formatter=format_asset_trackings
        )

def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{VS_TOOLS_PREFIX}_tracking",
        description="""
        Operations on tracking objects. 
        Use this when a user needs to poll the tracking to understand job status or the asset upload status.
        Actions:
        - read: Read a Tracking. Get the information of a tracking. Used for virtual service deploy/stop/configure tracking.
            args(dict): Dictionary with the following required parameters:
                tracking_id (str): Mandatory. The id of the tracking, must be a valid UUID.
        - read_asset_tracking: Read an Asset Tracking. Get the information of a tracking. Used only for asset upload tracking.
            args(dict): Dictionary with the following required parameters:
                tracking_id (str): Mandatory. The id of the tracking, must be a valid UUID.
        Tracking Schema:
        """ + str(MasterTracking.model_json_schema())
    )
    async def tracking(action: str, args: Dict[str, Any], ctx: Context) -> BaseResult:
        tracking_manager = TrackingManager(token, ctx)
        try:
            match action:
                case "read":
                    return await tracking_manager.read(args["tracking_id"])
                case "read_asset_tracking":
                    return await tracking_manager.read_asset_tracking(args["tracking_id"])
                case _:
                    return BaseResult(
                        error=f"Action {action} not found in tracking manager tool"
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
