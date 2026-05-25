import traceback
from typing import Optional, Dict, Any

import httpx
from mcp.server.fastmcp import Context

from sv_mcp.config.blazemeter import VS_TOOLS_PREFIX, VS_TRACKINGS_ENDPOINT
from sv_mcp.config.token import BzmToken
from sv_mcp.formatters.tracking import format_trackings, format_asset_trackings
from sv_mcp.models.result import BaseResult
from sv_mcp.models.vs.trackings import MasterTracking
from sv_mcp.telemetry import run_tool
from sv_mcp.tools.utils import vs_api_request


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
        Use this tool to read or poll tracking status by tracking ID (UUID).
        Call this whenever you have a tracking ID and need to know the status or result of an async operation.
        Actions:
        - read: Read a Tracking. Get status and result of a virtual service deploy/stop/configure operation.
            args(dict): Dictionary with the following required parameters:
                tracking_id (str): Mandatory. The tracking UUID to read.
        - read_asset_tracking: Read an Asset Tracking. Get the status and result of an asset upload operation.
            Use this action — NOT `read` — when the tracking ID came from an asset upload (e.g. "read asset tracking info <uuid>").
            args(dict): Dictionary with the following required parameters:
                tracking_id (str): Mandatory. The tracking UUID to read.
        Tracking Schema:
        """ + str(MasterTracking.model_json_schema())
    )
    async def tracking(action: str, args: Dict[str, Any], ctx: Context) -> BaseResult:
        tracking_manager = TrackingManager(token, ctx)

        async def _dispatch():
            match action:
                case "read":
                    return await tracking_manager.read(args["tracking_id"])
                case "read_asset_tracking":
                    return await tracking_manager.read_asset_tracking(args["tracking_id"])
                case _:
                    return BaseResult(error=f"Action {action} not found in tracking manager tool")

        try:
            return await run_tool("virtual_services_tracking", action, ctx, _dispatch)
        except httpx.HTTPStatusError:
            return BaseResult(error=f"Error: {traceback.format_exc()}")
        except Exception:
            return BaseResult(
                error=f"""Error: {traceback.format_exc()}
                          If you think this is a bug, please contact BlazeMeter support or report issue at https://github.com/BlazeMeter/bzm-mcp/issues"""
            )
