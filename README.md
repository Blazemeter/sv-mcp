# BlazeMeter Service Virtualization MCP Server

The BlazeMeter Service Virtualization MCP Server connects AI tools directly to BlazeMeter's Service Virtualization platform. 
This gives AI agents, assistants, and chatbots the ability to manage complete workflows from creation of transactions 
to deploying it to the virtual service. All through natural language interactions.

## Use Cases

- **Service Management**: Create and manage services.
- **Transaction Management**: Create, validate, manage HTTP and Messaging transactions.
- **Action Management**: Create, validate, manage transaction actions (Http calls and Webhooks).
- **Asset Management**: Upload assets (certificates and keystores).
- **Sandbox Management**: Attach HTTP transaction and test it.
- **Location Management**: List available locations.
- **Configuration Management**: Create and manage configurations for virtual services.
- **Virtual Service Management**: Create, modify, deploy, stop a virtual service, track its status.
- **Messaging Virtual Service Management**: Create, deploy, and manage messaging virtual services across IBM MQ, ActiveMQ, and Kafka brokers.
- **Recording Management**: Capture live broker traffic into recordings and replay them via messaging virtual services.
- **Virtual Service Templates Management**: Create, modify, create from the virtual service, apply to a virtual service.
- **Test Data Management**: Create, update, and read TDM datasets for virtual services to drive data-driven transaction matching.

---

## Prerequisites

- BlazeMeter API credentials (API Key ID and Secret)
- Compatible MCP host (VS Code, Claude Desktop, Cursor, Windsurf, etc.)
- Docker (only for Docker-based deployment)

## Setup

### **Get BlazeMeter API Credentials**
Follow the [BlazeMeter API Keys guide](https://help.blazemeter.com/docs/guide/api-blazemeter-api-keys.html) to obtain your API keys as JSON.

> [!IMPORTANT]
> When downloading your API keys from BlazeMeter, save the `api-keys.json` file in the same folder where you'll place the MCP binary.

## Available Tools

The BlazeMeter MCP Server provides comprehensive access to BlazeMeter's API through the following tools:

| Tool                         | Purpose                             | Key Capabilities                                      |
|------------------------------|-------------------------------------|-------------------------------------------------------|
| **User**                     | Blazemeter User Information         | Get current user details, default account/workspace/project |
| **Account**                  | Blazemeter Account Management       | List accounts, check AI consent, read account details |
| **Workspace**                | Blazemeter Workspace Management     | Manage workspaces, check billing usage       |
| **Service**                  | Service Management                  | Create and manage services                            |
| **Http Transaction**         | Http Transaction Management         | Create, manage and validate http transactions         |
| **Messaging Transaction**    | Messaging Transaction Management    | Create, manage and validate messaging transactions    |
| **Action**                   | Action Management                   | Create, manage and transactions actions               |
| **Virtual service**          | Virtual Service Management          | Create, manage, deploy, stop virtual services         |
| **Virtual service template** | Virtual Service Template Management | Create, manage, apply to the virtual service          |
| **Messaging Virtual Service**| Messaging Virtual Service Management| Create, manage, deploy messaging virtual services for IBM MQ, ActiveMQ, Kafka |
| **Recording**                | Recording Management                | Create, manage recordings and recorded messages for messaging virtual services |
| **Asset**                    | Asset Management                    | Upload assets                                         |
| **Configuration**            | Configuration Management            | Create, manage configurations                         |
| **Sandbox**                  | Sandbox Management                  | Assign http transaction, test it                      |
| **Tracking**                 | Tracking Management                 | Fetch tracking status for virtual service actions     |
| **Test Data**                | Test Data Management                | Create, update, read TDM datasets for virtual services |
---

### **User Management**
**What it does:** Get information about BlazeMeter account and default settings.

| Action | What you get |
|--------|-------------|
| Get user info | Your username, default account, workspace, and project IDs |

---

### **Account Management**
**What it does:** Manage your BlazeMeter accounts and check permissions.

| Action | What you get |
|--------|-------------|
| Get account details | Account information and AI consent status |
| List accounts | All accounts you have access to |

---

### **Workspace Management**
**What it does:** Navigate and manage testing workspaces.

| Action | What you get |
|--------|-------------|
| Get workspace details | Workspace information and billing details |
| List workspaces | All workspaces in an account |

---

### **Service Management**
**What it does:**  Creates and manages services.

| Action                     | What you get                          |
|----------------------------|---------------------------------------|
| Create a new service       | A service with provided name          |
| Update an existing service | An updated service with provided name |
| Get service                | A workspace service information       |
| List services              | All services in a workspace           |

---

### **Http Transaction Management**
**What it does:** Creates, validates, and manages http transactions.

| Action                        | What you get                                          |
|-------------------------------|-------------------------------------------------------|
| Read an HTTP Transaction      | Reads HTTP Transaction details                        |
| Create a new HTTP transaction | Creates a new HTTP transaction                        |
| Update HTTP transaction       | Updates existing HTTP transaction                     |
| List all HTTP transactions    | Lists all HTTP transactions in a workspace or service |
| Validate template             | Validates handlebars template                         |
| Convert template              | Safely converts handlebars template to VS format      |
| Assign keystore               | Assign keystore asset to an existing transaction      |
| Assign certificate            | Assign certificate asset to an existing transaction   |

---

### **Messaging Transaction Management**
**What it does:** Creates, validates, and manages messaging transactions.

| Action                             | What you get                                                  |
|------------------------------------|---------------------------------------------------------------|
| Read a Messaging Transaction       | Reads Messaging Transaction details                           |
| Create a new Messaging transaction | Creates a new Messaging transaction with optional priority, tags, source/destination mapping, and sample body |
| Update Messaging transaction       | Updates existing Messaging transaction                        |
| List all Messaging transactions    | Lists all Messaging transactions in a workspace, service, or messaging virtual service |
| Validate template                  | Validates handlebars template                                 |
| Convert template                   | Safely converts handlebars template to VS format              |
| Assign keystore                    | Assign keystore asset to an existing Messaging transaction    |
| Assign certificate                 | Assign certificate asset to an existing Messaging transaction |

---

### **Action Management**
**What it does:** Creates actions for transaction.

| Action                      | What you get                                   |
|-----------------------------|------------------------------------------------|
| Create an HTTP Call         | Creates an HTTP Call sync action               |
| Create a Web Hook           | Creates a Webhook async                        |
| Assign keystore             | Assign keystore asset to an existing action    |
| Assign certificate          | Assign certificate asset to an existing action |

---

### **Asset Management**
**What it does:** Creates, lists, manages assets.

| Action                 | What you get                                              |
|------------------------|-----------------------------------------------------------|
| Read an Asset          | Reads Asset details                                       |
| List all Assets        | Lists all assets in a workspace                           |
| Upload asset file      | Creates an asset from user's file                         |
| Set keystore passwords | Sets passwords for existing certificate or keystore asset |

---

### **Configuration Management**
**What it does:** Creates, lists, manages configurations.

| Action                    | What you get                              |
|---------------------------|-------------------------------------------|
| Read a Configuration      | Reads Configuration details               |
| List all Configurations   | Lists all configurations in a workspace   |
| Create a Configuration    | Creates new configuration                 |
| Update a Configuration    | Adds new values to existing configuration |

---

### **Location Management**
**What it does:** Lists available locations.

| Action                 | What you get                              |
|------------------------|-------------------------------------------|
| List all locations     | Lists all locations in a workspace        |

---

### **Sandbox Management**
**What it does:** Validates HTTP transactions without deploying a virtual service.

| Action       | What you get                                                             |
|--------------|--------------------------------------------------------------------------|
| Init sandbox | Assigns an existing transaction to the sandbox                           |
| Test request | Sends test http request to the sandbox and receives transaction response |

---

### **Tracking Management**
**What it does:** Reads virtual service action tracking details.

| Action                        | What you get                                  |
|-------------------------------|-----------------------------------------------|
| Read a tracking               | Reads virtual service action tracking details |
| Read an asset uplaod tracking | Reads file upload tracking details            |

---
### **Virtual Service Management**
**What it does:** Create, manage, deploy, stop, update your virtual service.

| Action                         | What you get                                                                              |
|--------------------------------|-------------------------------------------------------------------------------------------|
| Read a Virtual Service         | Reads Virtual Service details                                                             |
| Create a new Virtual Service   | Creates a new Virtual Service with enabled HTTP runner                                    |
| Update Virtual Service         | Updates existing Virtual Service                                                          |
| List all Virtual Services      | Lists all Virtual Services in a workspace or service                                      |
| Deploy Virtual Service         | Starts Virtual Service container                                                          |
| Configure Virtual Service      | Updates running Virtual Service                                                           |
| Stop Virtual Service           | Stops Virtual Service container                                                           |
| Assign transactions            | Assigns transactions to the Virtual Service                                               |
| Unassign transactions          | Unassigns transactions from the Virtual Service                                           |
| Assign configuration           | Assigns configuration to the Virtual Service                                              |
| Apply Virtual Service Template | Applies Virtual Service Template settings to the Virtual Service                          |
| Set Proxy                      | Adds proxy settings to the Virtual Service                                                |
| Unset Proxy                    | Removes proxy settings from the Virtual Service                                           |
| Assign Keystore                | Assigns keystore asset to the Virtual Service                                             |
| Assign Keystore + Truststore   | Assigns keystore asset to the Virtual Service, to be used as both Keystore and Truststore |

---

### **Messaging Virtual Service Management**
**What it does:** Create, manage, deploy, stop messaging virtual services. Supports IBM MQ (JMS and Native), ActiveMQ Classic, ActiveMQ Artemis, and Kafka brokers.

| Action                    | What you get                                                                                      |
|---------------------------|---------------------------------------------------------------------------------------------------|
| Read a Virtual Service    | Reads Messaging Virtual Service details including broker config and protocol                      |
| Create a Virtual Service  | Creates a Messaging Virtual Service for any supported protocol with full broker configuration     |
| Update a Virtual Service  | Partially updates a Messaging Virtual Service (only provided fields change)                       |
| List all Virtual Services | Lists all Messaging Virtual Services in a workspace or service                                    |
| Deploy Virtual Service    | Starts Messaging Virtual Service container                                                        |
| Stop Virtual Service      | Stops Messaging Virtual Service container                                                         |
| Configure Virtual Service | Hot-reloads transactions into a running Messaging Virtual Service                                 |
| Assign transactions       | Assigns transactions to the Messaging Virtual Service                                             |
| Unassign transactions     | Unassigns transactions from the Messaging Virtual Service                                         |
| Assign recordings         | Assigns recordings to the Messaging Virtual Service for replay                                    |
| Unassign recordings       | Unassigns recordings from the Messaging Virtual Service                                           |
| Assign configuration      | Assigns configuration to the Messaging Virtual Service                                            |
| Set Proxy                 | Adds proxy settings to the Messaging Virtual Service                                              |
| Unset Proxy               | Removes proxy settings from the Messaging Virtual Service                                         |
| Assign queue              | Assigns a queue to the Messaging Virtual Service                                                  |
| Assign topic              | Assigns a topic to the Messaging Virtual Service                                                  |

**Supported protocols and required broker config fields:**

| Protocol           | hostname | port | channel | queueManager | username | password | SSL | Embedded broker | Kafka-specific |
|--------------------|----------|------|---------|--------------|----------|----------|-----|-----------------|----------------|
| IBM_MQ9_JMS        | ✓        | ✓    | ✓       | ✓            | ✓        | ✓        | ✓   | —               | —              |
| IBM_MQ9_NATIVE     | ✓        | ✓    | ✓       | ✓            | ✓        | ✓        | ✓   | —               | —              |
| ACTIVE_MQ_CLASSIC  | ✓        | ✓    | —       | —            | ✓        | ✓        | opt | ✓               | —              |
| ACTIVE_MQ_ARTEMIS  | ✓        | ✓    | —       | —            | ✓        | ✓        | opt | ✓               | —              |
| KAFKA              | ✓        | ✓    | —       | —            | opt      | opt      | opt | —               | autoOffsetReset, numPartitions |

---

### **Recording Management**
**What it does:** Creates and manages recordings of live broker traffic. Recordings can be attached to messaging virtual services for replay.

| Action               | What you get                                                                            |
|----------------------|-----------------------------------------------------------------------------------------|
| List recordings      | Lists all recordings in a workspace, optionally filtered by service or virtual service  |
| Read a recording     | Reads recording details including inline messages                                       |
| Create a recording   | Creates a new recording with optional runtime config (replayCount, delays)              |
| Update a recording   | Full replacement of a recording                                                         |
| Patch a recording    | Partial update — only provided fields change                                            |
| List messages        | Lists recorded messages within a recording, sorted by index                             |
| Create message       | Adds a recorded message to a recording (base64-encoded content)                         |
| Update message       | Full replacement of a recorded message                                                  |
| Patch message        | Partial update of a recorded message                                                    |

---
### **Virtual Service Template Management**
**What it does:** Create, manage virtual service templates.

| Action                                | What you get                                                                                       |
|---------------------------------------|----------------------------------------------------------------------------------------------------|
| Read a Virtual Service Template       | Reads Virtual Service Template details                                                             |
| Create a new Virtual Service Template | Creates a new Virtual Service Template                                                             |
| Update Virtual Service Template       | Updates existing Virtual Service Template                                                          |
| List all Virtual Service Templates    | Lists all Virtual Service Templates in a workspace or service                                      | |
| Assign transactions                   | Assigns transactions to the Virtual Service Template                                               |
| Unassign transactions                 | Unassigns transactions from the Virtual Service Template                                           |
| Assign configuration                  | Assigns configuration to the Virtual Service Template                                              |
| Assign Keystore                       | Assigns keystore asset to the Virtual Service Template                                             |
| Assign Keystore + Truststore          | Assigns keystore asset to the Virtual Service Template, to be used as both Keystore and Truststore |

---

### **Test Data Management**
**What it does:** Creates and manages TDM (Test Data Manager) datasets that drive data-driven transaction matching. Dataset fields are referenced in transaction DSLs using `${fieldName}` syntax.

| Action              | What you get                                                                     |
|---------------------|----------------------------------------------------------------------------------|
| Create from schema  | Creates a dataset by defining entities with field names and generator expressions |
| Create from CSV     | Creates a dataset from a local CSV file; entity name is `{stem}_csv`, fields use `valueOfCSV` generators |
| List                | Lists data-model assets in a workspace                                           |
| Read                | Reads a data-model asset with full content for a given service                   |
| Update              | Replaces entities/fields on an existing schema-based dataset                     |
| Update from CSV     | Rebuilds a CSV-based dataset from a local CSV file; supports field name remapping |

---

### Enabling or Disabling MCP Tools

The MCP server supports enabling or disabling specific tools at startup using the environment variable MCP_ENABLED_TOOLS.
If the environment variable is not set or is an empty string, all available tools are automatically enabled.

To enable only certain tools, set the environment variable to a comma-separated list of tool names.

Example:
MCP_ENABLED_TOOLS="blazemeter_user,blazemeter_account,virtual_services_virtual_service"

---

### Observability (OpenTelemetry)

The server emits one trace span per MCP tool call using [OpenTelemetry](https://opentelemetry.io/). Tracing is off by default and activates automatically when you set an OTLP endpoint.

**Enable tracing — environment variable:**

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
sv-mcp --mcp
```

**Enable tracing — CLI argument (binary / uvx):**

```bash
sv-mcp --mcp --otel-endpoint http://localhost:4318
```

The `--otel-endpoint` flag overrides `OTEL_EXPORTER_OTLP_ENDPOINT` when both are set.

**Passing authentication headers:**

```bash
# env var (comma-separated key=value pairs)
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer your-token"

# CLI flag (repeatable)
sv-mcp --mcp \
  --otel-endpoint http://your-collector:4318 \
  --otel-headers "Authorization=Bearer your-token" \
  --otel-headers "X-Dataset=sv-mcp"
```

**Disable tracing entirely:**

```bash
# env var
export OTEL_SDK_DISABLED=true

# CLI flag
sv-mcp --mcp --no-telemetry
```

Each span includes:
- `gen_ai.tool.name` — MCP tool name (e.g. `virtual_services_http_transaction`)
- `mcp.tool.action` — action dispatched (e.g. `create_and_test`)
- `mcp.client.name` / `mcp.client.version` — MCP client identity from the initialize handshake (when provided)
- `error.type` — set on failure (`auth_failed`, `not_found`, `rate_limited`, `server_error`, `timeout`, `tool_error`, `api_error`)

**W3C Trace Context propagation:** if your MCP client passes `traceparent`/`tracestate` in `_meta`, spans are linked to the parent trace automatically.

**SDK availability by deployment:**

| Deployment | OTel SDK bundled | What you need |
|---|---|---|
| Docker image | ✅ Yes | Pass `-e OTEL_EXPORTER_OTLP_ENDPOINT=...` at runtime |
| Standalone binary | ✅ Yes | `--otel-endpoint URL` arg or `OTEL_EXPORTER_OTLP_ENDPOINT` env var |
| uvx | ✅ Yes | `--otel-endpoint URL` arg or `OTEL_EXPORTER_OTLP_ENDPOINT` env var |
| pip install | ✅ Yes | Set `OTEL_EXPORTER_OTLP_ENDPOINT` env var |

**Docker:**

```bash
docker run --rm -i \
  -e API_KEY_ID=your_key_id \
  -e API_KEY_SECRET=your_key_secret \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://your-collector:4318 \
  sv-mcp
```

**pip:**

```bash
pip install sv-mcp
```

**uvx:**

```bash
uvx --from "git+https://github.com/Blazemeter/sv-mcp.git" sv-mcp \
  --otel-endpoint http://your-collector:4318
```

The server never crashes if the endpoint is unreachable or the SDK is not installed.

---

### **MCP Client Configuration using uvx (Recommended)**

[uvx](https://docs.astral.sh/uv/guides/tools/) installs and runs the package in an isolated environment — no manual setup required.

```json
{
  "mcpServers": {
    "blazemeter-sv": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/Blazemeter/sv-mcp.git",
        "sv-mcp"
      ],
      "env": {
        "API_KEY_PATH": "/path/to/api-key.json"
      }
    }
  }
}
```

To pin a specific version or branch, change the `--from` value:
- Tag: `git+https://github.com/Blazemeter/sv-mcp.git@v1.0.4`
- Branch: `git+https://github.com/Blazemeter/sv-mcp.git@main`

---

### **MCP Client Configuration for Local testing using VS Code or Claude Desktop**
   1. Run main.py with --mcp flag
   2. Configure your MCP client with the following settings:
```json
{
  "mcpServers": {
    "virtual services mcp": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "path to your python interpreter /.../venv/bin/python",
      "args": [
        "path to project main.py /.../sv_mcp/main.py",
        "--mcp"
      ],
      "env": {
        "API_KEY_PATH": "path to api key file /.../api-key.json"
      }
    }
  }
}
```

## Format of the Api key file  
          
```json
{
  "id": "your_api_key_id",
  "secret": "your_api_key_secret"
}
```
## Docker Support

### **MCP Client Configuration for Docker**
 Build dokcer image using the following command:
 ```docker build . -t vs-mcp:latest ```

```json
{
  "mcpServers": {
    "Docker BlazeMeter MCP": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e",
        "API_KEY_ID=your_api_key_id",
        "-e",
        "API_KEY_SECRET=your_api_key_secret",
        "-e",
        "SOURCE_WORKING_DIRECTORY=/tmp",
        "-e",
        "OTEL_EXPORTER_OTLP_ENDPOINT=http://your-collector:4318",
        "-v",
        "/host/path/to/your/test/files:/tmp",
        "us-docker.pkg.dev/verdant-bulwark-278/sv-mcp/sv-mcp:latest"
      ]
    }
  }
}
```
> [!IMPORTANT]
> For Windows OS, paths must use backslashes (`\`) and be properly escaped as double backslashes (`\\`) in the JSON configuration.
> E.g.: `C:\\User\\Desktop\\mcp_test_folder`

> [!NOTE]
> In order to obtain the `API_KEY_ID` and`API_KEY_SECRET` refere to [BlazeMeter API keys](https://help.blazemeter.com/docs/guide/api-blazemeter-api-keys.html)
