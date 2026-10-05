# BlazeMeter Service Virtualization MCP Server

The BlazeMeter Service Virtualization MCP Server connects AI tools directly to BlazeMeter's Service Virtualization platform. 
This gives AI agents, assistants, and chatbots the ability to manage complete workflows from creation of transactions 
to deploying it to the virtual service. All through natural language interactions.

## Use Cases

- **Service Management**: Create and manage services.
- **Transaction Management**: Create, validate, manage HTTP and Messaging transactions.
- **Action Management**: Create, read, list, update, delete, and reorder transaction actions (Http calls, Webhooks, and State Updates).
- **Asset Management**: Upload assets (certificates and keystores).
- **Sandbox Management**: Attach HTTP transaction and test it.
- **Location Management**: List available locations.
- **Configuration Management**: Create and manage configurations for virtual services.
- **Virtual Service Management**: Create, modify, deploy, stop a virtual service, track its status.
- **Messaging Virtual Service Management**: Create, deploy, and manage messaging virtual services across IBM MQ, ActiveMQ, and Kafka brokers.
- **Recording Management**: Capture live broker traffic into recordings and replay them via messaging virtual services.
- **Virtual Service Templates Management**: Create, modify, create from the virtual service, apply to a virtual service.
- **Test Data Management**: Create, update, and read TDM datasets and global variables for virtual services to drive data-driven transaction matching.
- **Stateful Virtual Services**: Store, update, and delete service data and maintain global counters with State Update actions, then inspect, export, and reset the live state of a virtual service.

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
| **Action**                   | Action Management                   | Create, read, list and manage transaction actions, including State Updates |
| **Virtual service**          | Virtual Service Management          | Create, manage, deploy, stop virtual services         |
| **Virtual service template** | Virtual Service Template Management | Create, manage, apply to the virtual service          |
| **Messaging Virtual Service**| Messaging Virtual Service Management| Create, manage, deploy messaging virtual services for IBM MQ, ActiveMQ, Kafka |
| **Recording**                | Recording Management                | Create, manage recordings and recorded messages for messaging virtual services |
| **Asset**                    | Asset Management                    | Upload assets                                         |
| **Configuration**            | Configuration Management            | Create, manage configurations                         |
| **Sandbox**                  | Sandbox Management                  | Assign http transaction, test it                      |
| **Tracking**                 | Tracking Management                 | Fetch tracking status for virtual service actions     |
| **Test Data**                | Test Data Management                | Create, update, read TDM datasets and global variables for virtual services |
| **State**                    | Virtual Service State Management    | Read, export, and reset the service data of a stateful virtual service |
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
**What it does:** Creates, reads, lists, updates, deletes, and reorders processing actions for a transaction. Processing actions run after a request matches and before the response is sent.

| Action                      | What you get                                                                                   |
|-----------------------------|------------------------------------------------------------------------------------------------|
| Read an Action              | Reads a single transaction action's details                                                    |
| List Actions                | Lists all actions of a transaction                                                             |
| Create an HTTP Call         | Creates an HTTP Call sync action                                                               |
| Create a Web Hook           | Creates a Webhook async                                                                        |
| Create a State Update       | Creates a State Update action that stores, updates, or deletes service data, or sets or increments a global variable |
| Update an Action            | Partially updates an action's name, definition, or conditions                                  |
| Delete an Action            | Deletes an action from a transaction                                                           |
| Reorder Actions             | Sets the execution order of a transaction's actions                                            |
| Assign keystore             | Assign keystore asset to an existing action                                                    |
| Assign certificate          | Assign certificate asset to an existing action                                                 |

Every create action accepts optional `conditions`; the action only runs when all of them match.

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
| Configure Virtual Service      | Updates running Virtual Service; optionally keeps or regenerates its service data (state) |
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
| Read global variables | Reads the service's global variables (global-scope parameters such as counters) |
| Set global variables  | Replaces the service's global variables, used as initial values for stateful virtual services |

---

### **Virtual Service State Management**
**What it does:** Inspects and resets the service data of a stateful virtual service. A virtual service becomes stateful when its transactions have State Update actions. State belongs to the virtual service, is shared by all of its clients, and persists across stop and start.

| Action            | What you get                                                                                         |
|-------------------|------------------------------------------------------------------------------------------------------|
| Read data         | Reads the virtual service's service data: download links and global variables                        |
| Export data       | Exports the running virtual service's current (state-modified) dataset; returns a tracking id        |
| Reset             | Reconfigures the running virtual service and regenerates its service data, discarding state changes  |

---

### Building a stateful virtual service

A typical end-to-end flow an AI assistant can run with these tools:

1. **Seed the data:** `virtual_services_test_data` → `create_from_schema` with the data entities and `global_variables` (e.g. `{"order_counter": "0"}`).
2. **Define the transactions:** `virtual_services_http_transaction` → `create` a `POST /orders` transaction and a `GET /orders?id=…` transaction whose response reads the stored rows with `${#each (blazeData 'orders' 'where …')}`.
3. **Make it stateful:** `virtual_services_action` → `create_state_update` on the POST transaction (store the order, increment `order_counter`). For a global variable the definition is `{"model": "", "filters": [], "parameters": [{"key": "order_counter", "value": "1"}], "objectAction": "INCREMENT_VALUE"}` (or `UPDATE_VALUE` to set it). To store a row, use `"model": "orders"`, `"objectAction": "STORE_OBJECT"` and one parameter per field. For update or delete object, add `"filters": [{"key": "id", "operation": "EQUALS", "values": ["${request.query.id}"]}]` to select the rows. The operations are `EQUALS`, `LESS_THAN`, `GREATER_THAN`, `STARTS_WITH`, `ENDS_WITH`, and `IN_LIST`.
4. **Deploy:** `virtual_services_virtual_service` → `create` + `deploy`.
5. **Inspect or reset:** `virtual_services_state` → `export_data` (track it) + `read_data`, or `reset`.

**Per-key state:** when the state is keyed by a value in the request (per user, device or order id), seed one row per key and let the matcher select the row:

1. `virtual_services_test_data` → `create_from_csv` with one row per key, e.g. columns `account_id,locked` (entity `accounts_csv`).
2. A read transaction with the URL matcher `equals_url` `/v1/accounts/${account_id}/status`. The request selects the row whose `account_id` is in the path, and the response reads that row with `${locked}`.
3. A write transaction with the same URL and `POST`, and a `create_state_update` action:
   ```json
   {"model": "accounts_csv",
    "filters": [{"key": "account_id", "operation": "EQUALS", "values": ["${account_id}"]}],
    "parameters": [{"key": "locked", "value": "${jsonPath request.body '$.locked'}"}],
    "objectAction": "UPDATE_OBJECT"}
   ```
   `${account_id}` in the filter value resolves to the matched row's value, so a write changes only that row.

Use `STORE_OBJECT` with `blazeData` reads instead when the rows are created at runtime.

---

### Enabling or Disabling MCP Tools

The MCP server supports enabling or disabling specific tools at startup using the environment variable MCP_ENABLED_TOOLS.
If the environment variable is not set or is an empty string, all available tools are automatically enabled.

To enable only certain tools, set the environment variable to a comma-separated list of tool names.

Example:
MCP_ENABLED_TOOLS="blazemeter_user,blazemeter_account,virtual_services_virtual_service"

---

### Observability (OpenTelemetry)

The server emits one trace span per MCP tool call using [OpenTelemetry](https://opentelemetry.io/). By default it exports over **gRPC** to the Perforce collector at `https://grpc.public.prd.shared.perforce.com`. No configuration is needed for shipped releases; set `OTEL_SDK_DISABLED=true` (or `--no-telemetry`) to turn it off.

**Override the destination — environment variable:**

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317   # gRPC (insecure for localhost)
sv-mcp --mcp
```

**Override the destination — CLI argument (binary / uvx):**

```bash
sv-mcp --mcp --otel-endpoint http://localhost:4317
```

The transport is always **gRPC** (OTLP/HTTP is not used). `OTEL_EXPORTER_OTLP_ENDPOINT` / `--otel-endpoint` overrides only the *destination URL*, not the protocol — and an `http://` scheme there simply means an insecure (no-TLS) gRPC channel, so always target the collector's gRPC port (`4317`), never its HTTP port (`4318`).

> A local verification stack (collector + Jaeger + Prometheus + Grafana) lives in [`integration/telemetry/`](integration/telemetry/) — `docker compose up`, then point the server at `http://localhost:4317`.

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

The SDK is bundled in every deployment and exports to the Perforce gRPC collector by default — nothing extra is required to get tracing. Override only if you want a different destination:

| Deployment | OTel SDK bundled | To redirect / disable |
|---|---|---|
| Docker image | ✅ Yes | `-e OTEL_EXPORTER_OTLP_ENDPOINT=...` or `-e OTEL_SDK_DISABLED=true` |
| Standalone binary | ✅ Yes | `--otel-endpoint URL` / `--no-telemetry` |
| uvx | ✅ Yes | `--otel-endpoint URL` / `--no-telemetry` |

**Docker (redirect to your own collector):**

```bash
docker run --rm -i \
  -e API_KEY_ID=your_key_id \
  -e API_KEY_SECRET=your_key_secret \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://your-collector:4317 \
  sv-mcp
```

**uvx:**

```bash
uvx --from "git+https://github.com/Blazemeter/sv-mcp.git" sv-mcp \
  --otel-endpoint http://your-collector:4317
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
