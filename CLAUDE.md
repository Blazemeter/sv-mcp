# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **BlazeMeter Service Virtualization MCP Server** — a Python MCP server that bridges AI tools (Claude, VS Code, Cursor) with BlazeMeter's cloud-based Service Virtualization API, enabling AI assistants to automate virtual service workflows.

## Commands

**Setup (uses `uv` package manager):**
```bash
uv sync              # production deps
uv sync --extra dev  # includes pytest and pytest-asyncio for testing
```

**Run the server:**
```bash
# STDIO mode (default for MCP clients)
python sv_mcp/main.py --mcp

# HTTP mode
python sv_mcp/main.py --http

# HTTP stateless mode
python sv_mcp/main.py --stateless

# With log level
python sv_mcp/main.py --mcp --log-level DEBUG
```

**Tests:**
```bash
PYTHONPATH=. pytest
# Single test file:
PYTHONPATH=. pytest tests/test_sandbox_formatter.py
PYTHONPATH=. pytest tests/test_create_and_test.py
# With JUnit output (CI):
PYTHONPATH=. pytest --junitxml=reports/junit-report.xml
```
Async tests use `pytest-asyncio` (dev dependency). `asyncio_mode = "auto"` is set in `pyproject.toml` so no per-test marks are needed.

**Build standalone binary:**
```bash
python build.py
```

**Docker:**
```bash
docker build -t sv-mcp .
docker run -e API_KEY_ID=<id> -e API_KEY_SECRET=<secret> sv-mcp
```

## Environment Variables

| Variable | Description |
|---|---|
| `API_KEY_PATH` | Path to `api-key.json` with `{"id": "...", "secret": "..."}` |
| `API_KEY_ID` / `API_KEY_SECRET` | Alternative to key file (used in Docker) |
| `MCP_MODE` | Override mode: `stdio`, `http`, `http-stateless` |
| `MCP_ENABLED_TOOLS` | Comma-separated tool names to enable (all enabled if unset) |
| `MCP_DOCKER` | Set `true` when running in Docker |

## Architecture

The codebase follows a layered architecture:

```
main.py           → Entry point: CLI args, token loading, FastMCP init
server.py         → Tool registration hub (respects MCP_ENABLED_TOOLS filtering)
tools/            → MCP tool implementations (async def register(mcp, token))
  utils.py        → Centralized httpx client (HTTP/2, basic auth, timeouts)
  vs/             → 14 Virtual Service tool managers
models/           → Pydantic data models
  result.py       → BaseResult wrapper (result, error, total, has_more, info, warning)
  vs/             → VS domain models (37 files)
    sandbox_response.py → SandboxResponse: matched bool + mismatch_reasons derived from matchingLog
formatters/       → Transform raw API responses into domain models
config/
  token.py        → BzmToken auth handling
  blazemeter.py   → API base URLs and constants
  path_mapper.py  → Docker/binary path mapping
```

**Two API base URLs** (defined in `config/blazemeter.py`):
- `BZM_API_BASE_URL`: `https://a.blazemeter.com/api/v4` — user/account/workspace operations
- `VS_API_BASE_URL`: `https://mock.blazemeter.com/api/v1` — virtual service operations

**Tool registration pattern:** Each manager in `tools/` and `tools/vs/` exports `async def register(mcp, token)`. `server.py` calls all of them, optionally filtered by `MCP_ENABLED_TOOLS`.

**Data flow:** MCP tool call → manager → `tools/utils.py` (httpx) → BlazeMeter API → formatter → Pydantic model → `BaseResult` response.

## Key Domain Concepts

The dependency hierarchy matters for tool usage:
```
accounts → workspaces → locations → services → transactions → virtual services
```

- Use `activeWorkspaceId` from the user object as default `workspace_id`
- `list_*` actions return minimal info; `read_*` actions return full details
- Transactions (HTTP or messaging) are defined before creating virtual services
- Sandbox testing validates HTTP transactions without deployment. Use `create_and_test` action (not `create`) when the DSL contains Handlebars templates — it creates the transaction and runs sandbox validation in one step. `SandboxResponse.matched` is `True` when the request matched; `mismatch_reasons` lists why it didn't when `matched=False`.

## Tool Categories (14 total)

Core: `blazemeter_user`, `blazemeter_account`, `blazemeter_workspaces`

Virtual Services: `virtual_services_service`, `virtual_services_http_transaction`, `virtual_services_messaging_transaction`, `virtual_services_virtual_service`, `virtual_services_virtual_service_template`, `virtual_services_action`, `virtual_services_asset`, `virtual_services_configuration`, `virtual_services_sandbox`, `virtual_services_location`, `virtual_services_tracking`

## Design Docs

Implementation specs and plans live in `docs/superpowers/`:
- `specs/` — approved design documents
- `plans/` — step-by-step implementation plans
