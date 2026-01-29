import argparse
import logging
import os
import sys
from typing import Literal, cast

from mcp.server.fastmcp import FastMCP

from vs_mcp.config.token import BzmToken, BzmTokenError
from vs_mcp.config.version import __version__, __executable__
from server import register_tools

BLAZEMETER_API_KEY_FILE_PATH = os.getenv('API_KEY_PATH')

LOG_LEVELS = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def init_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.CRITICAL)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
        force=True,
    )


def get_token():
    global BLAZEMETER_API_KEY_FILE_PATH

    # Verify if running inside Docker container
    is_docker = os.getenv('MCP_DOCKER', 'false').lower() == 'true'
    token = None

    local_api_key_file = os.path.join(os.path.dirname(__executable__), "api-key.json")
    if not BLAZEMETER_API_KEY_FILE_PATH and os.path.exists(local_api_key_file):
        BLAZEMETER_API_KEY_FILE_PATH = local_api_key_file

    if BLAZEMETER_API_KEY_FILE_PATH:
        try:
            token = BzmToken.from_file(BLAZEMETER_API_KEY_FILE_PATH)
        except BzmTokenError:
            # Token file exists but is invalid - this will be handled by individual tools
            pass
        except Exception:
            # Other errors (file not found, permissions, etc.) - also handled by tools
            pass
    elif is_docker:
        token = BzmToken(os.getenv('API_KEY_ID'), os.getenv('API_KEY_SECRET'))
    return token


def run(log_level: str = "DEBUG", mode: str = "stdio"):
    token = get_token()
    instructions = """
    # BlazeMeter Virtual Services MCP Server
    A comprehensive integration tool that provides AI assistants with full programmatic access to BlazeMeter's 
    cloud-based performance testing platform.
    Enables automated management of complete load testing workflows from creation to execution and reporting.
    Transforms enterprise-grade testing capabilities into an AI-accessible service for intelligent automation 
    of complex performance testing scenarios.
    
    General rules:
        - If you have the information needed to call a tool action with its arguments, do so.
        - Read action always get more information about a particular item than the list action, list only display minimal information.
        - Read the current user information at startup to learn the username, default account and workspace information.
        - Dependencies:
            accounts: It doesn't depend on anyone. In user you can access which is the default account, and in the list of accounts, you can see the accounts available to the user.
            workspaces: Workspaces belong to a particular account.
            locations: Locations belong to a particular workspace.
            services: Services belong to a particular workspace.
            transactions: Transactions belong to a particular service.
            actions: Actions belong to a particular service.
            virtual services: Virtual Services belong to a particular service.
        Important: 
            Use the user’s activeWorkspaceId from from user object for workspace_id in all api calls, where it is required
            unless user requested a specific workspace.
    """
    if mode == "stdio":
        mcp = FastMCP("blazemeter-mcp", instructions=instructions, log_level="DEBUG")
        register_tools(mcp, token)
        mcp.run(transport="stdio")
    elif mode in ("http", "http-stateless"):
        host = os.getenv("HOST", "0.0.0.0")
        raw_port = os.getenv("PORT", "8000")
        try:
            port = int(raw_port)
        except ValueError:
            port = 8000

        mcp = FastMCP(
            "blazemeter-mcp",
            instructions=instructions,
            log_level=cast(LOG_LEVELS, log_level),
            stateless_http=(mode == "http-stateless"),
            host=host,
            port=port
        )
        register_tools(mcp, token)
        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="bzm-mcp")

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    parser.add_argument("--mcp", action="store_true", help="Execute MCP Server in STDIO mode")
    parser.add_argument("--http", action="store_true", help="Execute MCP Server in HTTP mode")
    parser.add_argument("--stateless", action="store_true", help="Execute MCP Server in HTTP stateless mode")

    parser.add_argument(
        "--log-level",
        default="DEBUG",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )

    args = parser.parse_args()
    init_logging(args.log_level)

    # ---------------------------------------------------------
    # Determine effective mode:
    # 1. CLI flags override everything
    # 2. MCP_MODE env next
    # 3. Default = "stdio"
    # ---------------------------------------------------------
    cli_mode = None
    if args.mcp:
        cli_mode = "stdio"
    elif args.http:
        cli_mode = "http"
    elif args.stateless:
        cli_mode = "http-stateless"

    env_mode = os.getenv("MCP_MODE", "").strip().lower()

    if cli_mode:
        effective_mode = cli_mode
    elif env_mode in ("stdio", "http", "http-stateless"):
        effective_mode = env_mode
    else:
        effective_mode = "stdio"

    # ---------------------------------------------------------
    # Launch server
    # ---------------------------------------------------------
    if effective_mode == "stdio":
        logging.disable(logging.CRITICAL)
        run(log_level="CRITICAL", mode="stdio")

    elif effective_mode == "http":
        run(log_level=args.log_level.upper(), mode="http")

    elif effective_mode == "http-stateless":
        run(log_level=args.log_level.upper(), mode="http-stateless")

    else:
        raise ValueError(f"Invalid MCP_MODE: {effective_mode}")
