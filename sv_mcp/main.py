import argparse
import logging
import os
import sys
from typing import Literal, cast

from mcp.server.fastmcp import FastMCP

from sv_mcp.config.token import BzmToken, BzmTokenError
from sv_mcp.config.version import __version__, __executable__
from sv_mcp.server import register_tools
from sv_mcp.telemetry import init_telemetry

BANNER = f"""
╔══════════════════════════════════════════════════════╗
║       BlazeMeter Service Virtualization MCP          ║
║                    v{__version__:<32}║
╚══════════════════════════════════════════════════════╝
"""


API_KEY_GUIDE = """
  No API key found. Create a file named  api-key.json  in the same
  directory as this binary with the following content:

    {
      "id": "your-api-key-id",
      "secret": "your-api-key-secret"
    }

  To generate a key: BlazeMeter → ⚙ Settings → API Keys → Add Key.
  Copy the ID and Secret shown at creation time (secret is shown once).
"""


def print_banner(mode: str, token_loaded: bool) -> None:
    auth = "API key loaded" if token_loaded else "No API key found"
    print(BANNER, file=sys.stderr)
    print(f"  Mode : {mode}", file=sys.stderr)
    print(f"  Auth : {auth}", file=sys.stderr)
    if not token_loaded:
        print(API_KEY_GUIDE, file=sys.stderr)
    print("", file=sys.stderr)

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


def get_token(api_key_id: str | None = None, api_key_secret: str | None = None):
    global BLAZEMETER_API_KEY_FILE_PATH

    token = None

    if api_key_id and api_key_secret:
        return BzmToken(api_key_id, api_key_secret)

    local_api_key_file = os.path.join(os.path.dirname(__executable__), "api-key.json")
    cwd_api_key_file = os.path.join(os.getcwd(), "api-key.json")
    if not BLAZEMETER_API_KEY_FILE_PATH:
        if os.path.exists(local_api_key_file):
            BLAZEMETER_API_KEY_FILE_PATH = local_api_key_file
        elif os.path.exists(cwd_api_key_file):
            BLAZEMETER_API_KEY_FILE_PATH = cwd_api_key_file

    if BLAZEMETER_API_KEY_FILE_PATH:
        try:
            token = BzmToken.from_file(BLAZEMETER_API_KEY_FILE_PATH)
        except BzmTokenError:
            pass
        except Exception:
            pass
    elif os.getenv('API_KEY_ID') and os.getenv('API_KEY_SECRET'):
        token = BzmToken(os.getenv('API_KEY_ID'), os.getenv('API_KEY_SECRET'))
    return token


def run(log_level: str = "DEBUG", mode: str = "stdio"):
    init_telemetry("sv-mcp", __version__)
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
        HTTP transaction validation:
            - When creating HTTP transactions that contain Handlebars templates, always use
              create_and_test (not create). A transaction is only complete when matched=true.
            - If create_and_test returns matched=false, read mismatch_reasons in the result,
              fix the DSL using the update action, re-init with virtual_services_sandbox init,
              then re-test with virtual_services_sandbox test_request.
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


def main():
    parser = argparse.ArgumentParser(prog="sv-mcp")

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    parser.add_argument("--mcp", action="store_true", help="Execute MCP Server in STDIO mode")
    parser.add_argument("--http", action="store_true", help="Execute MCP Server in HTTP mode")
    parser.add_argument("--stateless", action="store_true", help="Execute MCP Server in HTTP stateless mode")

    auth_group = parser.add_argument_group("authentication", "API credentials (override env vars and api-key.json)")
    auth_group.add_argument("--api-key-id", metavar="ID", help="BlazeMeter API key ID (overrides API_KEY_ID)")
    auth_group.add_argument("--api-key-secret", metavar="SECRET", help="BlazeMeter API key secret (overrides API_KEY_SECRET)")

    parser.add_argument(
        "--log-level",
        default="DEBUG",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )

    otel_group = parser.add_argument_group("telemetry", "OpenTelemetry settings (override env vars)")
    otel_group.add_argument(
        "--otel-endpoint",
        metavar="URL",
        help="OTLP collector endpoint URL (overrides OTEL_EXPORTER_OTLP_ENDPOINT)"
    )
    otel_group.add_argument(
        "--otel-headers",
        metavar="KEY=VALUE",
        action="append",
        help="OTLP header (repeatable, e.g. --otel-headers Authorization=Bearer\\ token); overrides OTEL_EXPORTER_OTLP_HEADERS"
    )
    otel_group.add_argument(
        "--no-telemetry",
        action="store_true",
        help="Disable all OpenTelemetry tracing and metrics (sets OTEL_SDK_DISABLED=true)"
    )

    args = parser.parse_args()
    init_logging(args.log_level)

    if args.no_telemetry:
        os.environ["OTEL_SDK_DISABLED"] = "true"
    if args.otel_endpoint:
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = args.otel_endpoint
    if args.otel_headers:
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = ",".join(args.otel_headers)

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

    if args.api_key_id:
        os.environ["API_KEY_ID"] = args.api_key_id
    if args.api_key_secret:
        os.environ["API_KEY_SECRET"] = args.api_key_secret

    token_preview = get_token(args.api_key_id, args.api_key_secret)
    if getattr(sys, 'frozen', False) or (effective_mode == "stdio" and sys.stdin.isatty()):
        print_banner(mode=effective_mode, token_loaded=token_preview is not None)

    if effective_mode == "stdio" and sys.stdin.isatty():
        print(
            "  stdin is a terminal — the MCP STDIO transport expects a client to speak\n"
            "  the MCP protocol over stdin/stdout. Run with --http or --stateless for\n"
            "  a standalone HTTP server, or configure your MCP client to launch this\n"
            "  process (e.g. Claude Desktop, Cursor).\n",
            file=sys.stderr,
        )
        sys.exit(0)

    if effective_mode == "stdio":
        logging.disable(logging.CRITICAL)
        run(log_level="CRITICAL", mode="stdio")
    elif effective_mode == "http":
        run(log_level=args.log_level.upper(), mode="http")
    elif effective_mode == "http-stateless":
        run(log_level=args.log_level.upper(), mode="http-stateless")
    else:
        raise ValueError(f"Invalid MCP_MODE: {effective_mode}")


if __name__ == "__main__":
    main()
