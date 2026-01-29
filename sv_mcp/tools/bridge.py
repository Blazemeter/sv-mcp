from mcp.server.fastmcp import Context

from sv_mcp.config.token import BzmToken
from sv_mcp.models.result import BaseResult


# NOTE: Imports are performed locally in each method to avoid cyclical import problems.
# This file currently acts as a bridge between different managers to access specific methods,
# primarily for validation of reference elements.
# BZM
async def read_account(token: BzmToken, ctx: Context, account_id: int) -> BaseResult:
    from sv_mcp.tools.account_manager import AccountManager
    return await AccountManager(token, ctx).read(account_id)


async def read_workspace(token: BzmToken, ctx: Context, workspace_id: int) -> BaseResult:
    from sv_mcp.tools.workspace_manager import WorkspaceManager
    return await WorkspaceManager(token, ctx).read(workspace_id)
