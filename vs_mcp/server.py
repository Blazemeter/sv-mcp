from vs_mcp.tools.user_manager import register as register_user_manager
from vs_mcp.tools.workspace_manager import register as register_workspace_manager
from vs_mcp.tools.account_manager import register as register_account_manager
from vs_mcp.tools.vs.service_manager import register as register_service_manager
from vs_mcp.tools.vs.http_transaction_manager import register as http_register_transaction_manager
from vs_mcp.tools.vs.messaging_transaction_manager import register as messaging_register_transaction_manager
from vs_mcp.tools.vs.virtual_service_manager import register as register_virtual_service_manager
from vs_mcp.tools.vs.virtual_service_template_manager import register as register_virtual_service_template_manager
from vs_mcp.tools.vs.tracking_manager import register as register_tracking_manager
from vs_mcp.tools.vs.asset_tracking_manager import register as register_asset_tracking_manager
from vs_mcp.tools.vs.location_manager import register as register_location_manager
from vs_mcp.tools.vs.sandbox_manager import register as register_sandbox_manager
from vs_mcp.tools.vs.action_manager import register as register_action_manager
from vs_mcp.tools.vs.configuration_manager import register as register_configuration_manager
from vs_mcp.tools.vs.asset_manager import register as register_asset_manager
from vs_mcp.config.token import BzmToken
from typing import Optional


def register_tools(mcp, token: Optional[BzmToken]):
    """
    Register all available tools with the MCP server.
    
    Args:
        mcp: The MCP server instance
        token: Optional BlazeMeter token (can be None if not configured)
    """
    register_user_manager(mcp, token)
    register_workspace_manager(mcp, token)
    register_account_manager(mcp, token)
    # register vs tools
    register_service_manager(mcp, token)
    http_register_transaction_manager(mcp, token)
    messaging_register_transaction_manager(mcp, token)
    register_virtual_service_manager(mcp, token)
    register_virtual_service_template_manager(mcp, token)
    register_tracking_manager(mcp, token)
    register_asset_tracking_manager(mcp, token)
    register_location_manager(mcp, token)
    register_sandbox_manager(mcp, token)
    register_action_manager(mcp, token)
    register_configuration_manager(mcp, token)
    register_asset_manager(mcp, token)
