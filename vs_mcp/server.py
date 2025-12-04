import os

from vs_mcp.tools.user_manager import register as register_user_manager
from vs_mcp.tools.workspace_manager import register as register_workspace_manager
from vs_mcp.tools.account_manager import register as register_account_manager
from vs_mcp.tools.vs.service_manager import register as register_service_manager
from vs_mcp.tools.vs.http_transaction_manager import register as http_register_transaction_manager
from vs_mcp.tools.vs.messaging_transaction_manager import register as messaging_register_transaction_manager
from vs_mcp.tools.vs.virtual_service_manager import register as register_virtual_service_manager
from vs_mcp.tools.vs.virtual_service_template_manager import register as register_virtual_service_template_manager
from vs_mcp.tools.vs.tracking_manager import register as register_tracking_manager
from vs_mcp.tools.vs.location_manager import register as register_location_manager
from vs_mcp.tools.vs.sandbox_manager import register as register_sandbox_manager
from vs_mcp.tools.vs.action_manager import register as register_action_manager
from vs_mcp.tools.vs.configuration_manager import register as register_configuration_manager
from vs_mcp.tools.vs.asset_manager import register as register_asset_manager
from vs_mcp.config.token import BzmToken
from typing import Optional, Dict, Callable


def register_tools(mcp, token: Optional[BzmToken]):
    """
    Register tools with the MCP server.
    If MCP_ENABLED_TOOLS is not set or empty, all tools are registered.
    If it is set, only tools listed (comma-separated) will be registered.
    """
    raw = os.getenv("MCP_ENABLED_TOOLS")

    # If no env var → enable all tools
    if raw is None or raw.strip() == "":
        enabled_set = None
    else:
        enabled_set = {name.strip().lower() for name in raw.split(",")}

    registry: Dict[str, Callable[[object, Optional[BzmToken]], None]] = {
        "user_manager": register_user_manager,
        "workspace_manager": register_workspace_manager,
        "account_manager": register_account_manager,
        "service_manager": register_service_manager,
        "http_transaction_manager": http_register_transaction_manager,
        "messaging_transaction_manager": messaging_register_transaction_manager,
        "virtual_service_manager": register_virtual_service_manager,
        "virtual_service_template_manager": register_virtual_service_template_manager,
        "tracking_manager": register_tracking_manager,
        "location_manager": register_location_manager,
        "sandbox_manager": register_sandbox_manager,
        "action_manager": register_action_manager,
        "configuration_manager": register_configuration_manager,
        "asset_manager": register_asset_manager,
    }

    for name, register_fn in registry.items():
        if enabled_set is None or name in enabled_set:
            register_fn(mcp, token)
