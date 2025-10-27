from typing import Optional

from mcp.server.fastmcp import Context

from vs_mcp.config.blazemeter import EXECUTIONS_ENDPOINT
from vs_mcp.config.token import BzmToken
from vs_mcp.tools import bridge
from vs_mcp.tools.utils import bzm_api_request


class ReportManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def read_summary(self, master_id: int):
        # Check if it's valid or allowed
        execution_result = await bridge.read_execution(self.token, self.ctx, master_id)
        if execution_result.error:
            return execution_result

        return await bzm_api_request(
            self.token,
            "GET",
            f"{EXECUTIONS_ENDPOINT}/{master_id}/reports/default/summary")

    async def read_error(self, master_id: int):
        """
        Get error report for a given master_id with client-side paging.
        Always returns paged results for AI efficiency.
        """
        # Check if it's valid or allowed
        execution_result = await bridge.read_execution(self.token, self.ctx, master_id)
        if execution_result.error:
            return execution_result

        return await bzm_api_request(
            self.token,
            "GET",
            f"{EXECUTIONS_ENDPOINT}/{master_id}/reports/errorsreport/data"
        )

    async def read_request_stats(self, master_id: int):
        """
        Get request statistics report for a given master_id with client-side paging.
        Always returns paged results for AI efficiency.
        """
        # Check if it's valid or allowed
        execution_result = await bridge.read_execution(self.token, self.ctx, master_id)
        if execution_result.error:
            return execution_result

        return await bzm_api_request(
            self.token,
            "GET",
            f"{EXECUTIONS_ENDPOINT}/{master_id}/reports/aggregatereport/data"
        )
