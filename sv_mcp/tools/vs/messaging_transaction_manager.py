import base64
from typing import Optional, Dict, Any, Annotated, List

import httpx
from mcp.server.fastmcp import Context

from sv_mcp.config.blazemeter import VS_TRANSACTIONS_ENDPOINT, WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX, VS_VALIDATIONS_ENDPOINT, \
    VS_CONVERT_ENDPOINT
from sv_mcp.config.token import BzmToken
from sv_mcp.formatters.transaction import format_messaging_transactions
from sv_mcp.formatters.validations import format_validation_request
from sv_mcp.models.result import BaseResult
from sv_mcp.models.vs.messaging_transaction import MessagingTransaction
from sv_mcp.telemetry import run_tool
from sv_mcp.tools.utils import vs_api_request, error_result


class MessagingTransactionManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def read(self, workspace_id: int, transaction_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{transaction_id}",
            result_formatter=format_messaging_transactions
        )

    async def list(self, workspace_id: int, service_id: Optional[int] = None,
                   limit: int = 50, offset: int = 0,
                   service_mock_id: Optional[int] = None) -> BaseResult:
        parameters = {
            "limit": limit,
            "skip": offset,
            "type": "MESSAGING"
        }
        if service_id is not None:
            parameters["serviceId"] = service_id
        if service_mock_id is not None:
            parameters["serviceMockId"] = service_mock_id
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}",
            result_formatter=format_messaging_transactions,
            params=parameters)

    async def create(self, transaction_name: str, workspace_id: int, service_id: int,
                     type: str, dsl, delay: Optional[int],
                     description: Optional[str] = None,
                     tags: Optional[List[str]] = None,
                     priority: Optional[int] = None,
                     messaging_transaction_mappings: Optional[dict] = None,
                     sample_body: Optional[str] = None) -> BaseResult:
        dsl_dict = dsl.model_dump() if hasattr(dsl, "model_dump") else dsl
        dsl_dict.setdefault("type", "MESSAGING")
        MessagingTransactionManager._normalize_dsl_content(dsl_dict)
        request = dsl_dict.get("requestDsl")
        if request:
            for body_matcher in request.get("body", []):
                value = body_matcher.get("matchingValue")
                if value is not None:
                    body_matcher["matchingValue"] = MessagingTransactionManager.to_base64(value)
        if delay:
            response = dsl_dict.get("responseDsl")
            if response:
                response["responseDelay"] = {
                    "type": "FIXED",
                    "duration": delay
                }
        txn: Dict[str, Any] = {
            "serviceId": service_id,
            "type": type,
            "dsl": dsl_dict,
            "name": transaction_name,
        }
        if description is not None:
            txn["description"] = description
        if tags is not None:
            txn["tags"] = tags
        if priority is not None:
            txn["priority"] = priority
        if messaging_transaction_mappings is not None:
            txn["messagingTransactionMappings"] = messaging_transaction_mappings
        if sample_body is not None:
            txn["sampleBody"] = sample_body
        transaction_body = {"transactions": [txn]}
        parameters = {
            "serviceId": service_id,
        }
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}",
            result_formatter=format_messaging_transactions,
            json=transaction_body,
            params=parameters
        )

    async def update(self, id: int, transaction_name: str, workspace_id: int,
                     type: str, dsl, delay: Optional[int],
                     description: Optional[str] = None,
                     tags: Optional[List[str]] = None,
                     priority: Optional[int] = None,
                     messaging_transaction_mappings: Optional[dict] = None,
                     sample_body: Optional[str] = None) -> BaseResult:
        dsl_dict = dsl.model_dump() if hasattr(dsl, "model_dump") else dsl
        dsl_dict.setdefault("type", "MESSAGING")
        MessagingTransactionManager._normalize_dsl_content(dsl_dict)

        body: Dict[str, Any] = {
            "id": id,
            "type": type,
            "dsl": dsl_dict,
            "name": transaction_name,
        }
        if description is not None:
            body["description"] = description
        if tags is not None:
            body["tags"] = tags
        if priority is not None:
            body["priority"] = priority
        if messaging_transaction_mappings is not None:
            body["messagingTransactionMappings"] = messaging_transaction_mappings
        if sample_body is not None:
            body["sampleBody"] = sample_body
        return await vs_api_request(
            self.token,
            "PUT",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{id}",
            result_formatter=format_messaging_transactions,
            json=body
        )

    async def assign_asset(self, id: int, workspace_id: int, type: str, assetId: int, alias: str) -> BaseResult:
        assert_type_body = {
            "assetId": assetId,
            "usageType": type,
            "alias": alias
        }
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{id}/assign-asset",
            result_formatter=format_messaging_transactions,
            json=assert_type_body
        )

    async def validate_template(self, template: str) -> BaseResult:
        validation_body = {
            "template": template,
        }
        return await vs_api_request(
            self.token,
            "POST",
            f"{VS_VALIDATIONS_ENDPOINT}",
            result_formatter=format_validation_request,
            json=validation_body
        )

    async def convert_template(self, template: str, encode=True) -> BaseResult:
        validation_body = {
            "template": template,
        }
        parameters = {
            "encode": encode
        }
        return await vs_api_request(
            self.token,
            "POST",
            f"{VS_CONVERT_ENDPOINT}",
            result_formatter=format_validation_request,
            json=validation_body,
            params=parameters
        )

    def to_base64(input_str: str) -> str:
        encoded_bytes = base64.b64encode(input_str.encode('utf-8'))
        encoded_str = encoded_bytes.decode('utf-8')
        return encoded_str

    @staticmethod
    def _normalize_dsl_content(dsl_dict: dict) -> None:
        """Ensure responseDsl.content is valid base64. Auto-encodes plain text in place."""
        response_dsl = dsl_dict.get("responseDsl")
        if not isinstance(response_dsl, dict):
            return
        content = response_dsl.get("content")
        if not content:
            return
        try:
            base64.b64decode(content + '=' * (-len(content) % 4), validate=True)
        except Exception:
            response_dsl["content"] = base64.b64encode(content.encode('utf-8')).decode('utf-8')


def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{VS_TOOLS_PREFIX}_messaging_transaction",
        description="""
        Operations on JMS Messaging transactions. 
        Use this when a user needs to create or select a JMS messaging transaction.
        DSL type field is mandatory and must be set to "MESSAGING".
      1. General Rules:
            - Supported JMS header names: 'MQ9_MQMD_VERSION', 'MQ9_MQMD_REPORT', 'MQ9_MQMD_MESSAGE_TYPE', 
                'MQ9_MQMD_EXPIRY', 'MQ9_MQMD_FEEDBACK', 'MQ9_MQMD_ENCODING', 'MQ9_MQMD_CHARACTER_SET', 
                'MQ9_MQMD_PRIORITY', 'MQ9_MQMD_PERSISTENCE', 'MQ9_MQMD_MESSAGE_ID', 'MQ9_MQMD_CORRELATION_ID', 
                'MQ9_MQMD_BACKOUT_COUNT', 'MQ9_MQMD_USER_ID', 'MQ9_MQMD_ACCOUNTING_TOKEN', 'MQ9_MQMD_APPLICATION_ID', 
                'MQ9_PUT_APPLICATION_TYPE', 'MQ9_PUT_APPLICATION_NAME', 'MQ9_PUT_DATE_TIME', 
                'MQ9_MQMD_APPLICATION_ORIGIN_DATA', 'MQ9_MQMD_GROUP_ID', 'MQ9_MQMD_SEQUENCE_NUMBER', 
                'MQ9_MQMD_OFFSET', 'MQ9_MQMD_FLAGS', 'MQ9_MQMD_ORIGINAL_LENGTH', 'JMS_MESSAGE_ID', 
                'JMS_CORRELATION_ID', 'JMS_TIMESTAMP', 'JMS_DELIVERY_MODE', 'JMS_REDELIVERED', 
                'JMS_EXPIRATION', 'JMS_PRIORITY'
            - Assign intermediate values with {{#assign "varName"}}{{value}}{{/assign}}.
            - Keep JSON objects outside helper calls; helpers should only produce values.
            - Do not nest helpers more than 1–2 levels deep.
            - Each helper must have exactly one opening and one closing brace; do not add extra # or braces.
            - Conditional helpers ({{#eq}}, {{#neq}}, {{#gt}}, {{#lt}}, etc.) must use variable names directly without quotes.
            - Use {{else}} only once per conditional; do not use {{#else}} or {{/else}}.
            - Avoid repeating the same condition in multiple nested blocks.
            - Templates must be valid JSON and readable.
            2. Explicit Helper Syntax:
            - Opening a block helper: {{#helperName [arguments]}}
              Example: {{#assign "userId"}} or {{#eq userId "0"}}
            - Closing a block helper: {{/helperName}}
              Example: {{/assign}} or {{/eq}}
            - Else clause: {{else}} (no #, no /)
              Example:
                {{#eq userId "0"}}
                  { "error": "User not found" }
                {{else}}
                  { "id": {{userId}}, "name": "John Doe" }
                {{/eq}}
            - Variable interpolation inside JSON: {{variableName}} only for values
            - JSON objects stay outside helpers.
            3. Fields that support templates:
            - ResponseDsl.content: Base64 encoded response body that can include templates using {{}} syntax.
            4. Available helpers (WireMock + Blazemeter custom helpers) — all use {{}} style:
            5. LLM-Specific Best Practices:
            - Produce one helper per line.
            - Do not combine multiple logic operations in a single line.
            - Use sequential conditionals for multiple branches instead of deeply nested {{#eq}} blocks.
            - Keep templates simple, granular, and maintainable.
            - Always follow the explicit helper syntax rules above to prevent extra braces or invalid {{#else}} usage.
            6. Example Templates:
            # --- Assigning and Joining Values ---
            {{#assign 'operation'}}{{join request.method request.url ' '}}{{/assign}}
            Result: {{operation}}
            
            # --- Headers ---
            All headers: {{request.headers}}
            Single header: {{request.headers.JMS_CORRELATION_ID}}
            Iterate headers:
            {{#each request.headers as |hdr|}}
            {{hdr.name}}: {{hdr.value}}
            {{/each}}
            
            # --- Body and Body Parsing ---
            Raw body: {{request.body}}
            Body as JSON: {{jsonPath request.body '$'}}
            Body as XML: {{xpath request.body '//element'}}
            Extract value using JSONPath:
            {{#assign 'price'}}{{jsonPath request.body '$.price'}}{{/assign}}
            Extracted price: {{price}}
            Extract value using XPath:
            {{#assign 'id'}}{{xpath request.body '//order/id/text()'}}{{/assign}}
            Extracted ID: {{id}}
            
            # --- Conditional Logic ---
            {{#eq request.headers.JMS_CORRELATION_ID '1234'}}
            Order is pending
            {{else}}
            Order status: {{request.headers.STATUS}}
            {{/eq}}
            
            # --- Arrays and Ranges ---
            {{#assign 'a'}}{{array 'A' 'B' 'C'}}{{/assign}}
            Joined: {{arrayJoin ',' a}}
            {{#assign 'b'}}{{arrayAdd a 'D' position=1}}{{/assign}}
            Added: {{arrayJoin ',' b}}
            {{#assign 'c'}}{{arrayRemove b position=2}}{{/assign}}
            Removed: {{arrayJoin ',' c}}
            
            {{#each (range 1 3) as |i|}}
            Item {{i}}
            {{/each}}
            
            # --- String Helpers ---
            {{join 'Order' request.path.1 'confirmed'}}
            {{replace 'foo-bar' '-' '_'}}
            {{upper request.method}}
            {{lower user.role}}
            {{capitalize 'hello world'}}
            {{capitalizeFirst 'wiremock templates'}}
            {{defaultIfEmpty request.headers.comment 'none'}}
            {{cut 'a,b,c' ','}}
            {{slugify 'Hello World!'}}
            {{stripTags '<b>bold</b>'}}
            {{substring 'abcdef' 2 5}}
            {{ljust 'hi' size=5 pad='*'}}
            {{rjust 'ok' size=5 pad='-'}}
            
            # --- Date and Time ---
            Requested at: {{now}}
            Formatted date: {{dateFormat now 'yyyy-MM-dd HH:mm:ss'}}
            
            # --- Math and Size ---
            {{#assign 'qty'}}{{jsonPath request.body '$.quantity'}}{{/assign}}
            {{#assign 'total'}}{{math price '*' qty}}{{/assign}}
            Total: {{total}}
            Item count: {{size request.headers.items}}
            
            # --- Regex Extraction ---
            {{#assign 'num'}}{{regexExtract request.path.1 '([0-9]+)'}}{{/assign}}
            Extracted number: {{num}}
            
            # --- Using "with" Context ---
            {{#with request.headers}}
            User-Agent: {{User-Agent}}
            {{/with}}
            
            # --- Available Request Parts Summary ---
            request.headers → Map of headers
            request.headers.NAME → Header value(s)
            request.properties → Map of headers
            request.properties.NAME → Header value(s)
            request.body → Raw request body (string)
            # --- Available Http Call Action Templates ---
            httpcalls.actionName.response.body → Response body of the http call action named "actionName"
            httpcalls.actionName.response.statuscode → Status code of the http call action named "actionName"
            httpcalls.actionName.request.url → Request URL of the http call action named "actionName"
            httpcalls.actionName.request.method → Request method of the http call action named "actionName
            httpcalls.actionName.request.headers → Request headers of the http call action named "actionName"
            httpcalls.actionName.request.body → Request body of the http call action named "actionName
             # --- Available Virtual Service Configuration Templates ---
            config.var1 → Value of the virtual service configuration parameter named "var1"
            
            # --- Error Handling Notes ---
            If the response returns raw unparsed template text (for example, showing {{request.body}} instead of the actual value), it means the template syntax is **invalid or malformed** and WireMock skipped template parsing.  
            If the response returns **HTTP 500** with an exception in the WireMock logs, it means the syntax was **parsed correctly but failed during runtime execution** (for example, referencing a non-existent variable, invalid JSONPath, or invalid helper argument).
            # --- Important Notes ---
            Each helper must always be opened and closed when block form is used (e.g. {{#assign ...}}{{/assign}}, {{#eq ...}}{{/eq}}, {{#each ...}}{{/each}}).  
            Inline helpers like {{join ...}}, {{replace ...}}, {{upper ...}}, {{jsonPath ...}} do not require closing tags.
        Actions:
        - read: Read a Transaction. Get the information of a transaction.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list transactions from.
                id (int): Mandatory. The id of the transaction to get information.
        - list: List all transactions.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list transactions from.
                serviceId (int): Optional. The id of the service to list transactions from. Without this it will list all transactions in the workspace.
                virtual_service_id (int): Optional. Filter by virtual service (messaging service mock) id.
                limit (int, default=10, valid=[1 to 50]): The number of transactions to list.
                offset (int, default=0): Number of transactions to skip.
        - validate_template: Validates template used in transaction definition.
            args:
                template (str): Mandatory. The handlebars template to validate.
        - convert_template: Converts template to blazemeter format.
            args:
                template (str): Mandatory. The handlebars template to validate.
                encode (bool, default=True): Whether to encode the converted template to Base64.
        - create: Create a new transaction.
            Important: before using template in transaction definition validate it and 
            convert it first using validate_template and convert_template actions.
            args(Transaction): A Transaction object with the following fields:
                name (str): Mandatory. The name of the transaction.
                serviceId (int): Mandatory. The id of the service to create the transaction in.
                type (str): Mandatory. The type of the transaction.
                dsl (MessagingDsl): Mandatory. The DSL definition of the transaction.
                workspace_id (int): Mandatory. The id of the workspace.
                delay (int): Optional. Response delay in milliseconds.
                description (str): Optional.
                tags (list[str]): Optional.
                priority (int): Optional. Matching priority 1–2147483647, default 10.
                messagingTransactionMappings (dict): Optional. {sourceName, sourceType, destinations: [{destinationName, destinationType}]}.
                sampleBody (str): Optional. Example request body for documentation.
        - update: Updates a certain transaction.
            Important: before using template in transaction definition validate it and  
            convert it first using validate_template and convert_template actions.
            args(Transaction): A Transaction object with the following fields:
                id (int): Mandatory. The id of the transaction.
                name (str): Mandatory. The new name of the transaction.
                type (str): Mandatory. The type of the transaction.
                dsl (MessagingDsl): Mandatory. The DSL definition of the transaction.
                workspace_id (int): Mandatory. The id of the workspace.
                delay (int): Optional. Response delay in milliseconds.
                description (str): Optional.
                tags (list[str]): Optional.
                priority (int): Optional. Matching priority 1–2147483647, default 10.
                messagingTransactionMappings (dict): Optional. {sourceName, sourceType, destinations: [{destinationName, destinationType}]}.
                sampleBody (str): Optional. Example request body for documentation.
        - assign_keystore: Assign keystore asset to the transaction.
            args(dict):
                id (int): Mandatory. The id of the transaction.
                asset_id (int): Mandatory. The id of the keystore asset to assign.
                alias (str): Mandatory. The certificate alias to use.
                workspace_id (int): Mandatory. The id of the workspace.  
        - assign_certificate: Assign certificate asset to the transaction.
            args(dict):
                id (int): Mandatory. The id of the transaction.
                asset_id (int): Mandatory. The id of the certificate asset to assign.
                workspace_id (int): Mandatory. The id of the workspace.           

        Transaction Schema (including full MessagingDsl with MessagingRequestDsl and MessagingResponseDsl):
        """ + str(MessagingTransaction.model_json_schema())
    )
    async def transaction(
            action: str,
            args: Annotated[Dict[str, Any], MessagingTransaction.model_json_schema()],
            ctx: Context
    ) -> BaseResult:
        transaction_manager = MessagingTransactionManager(token, ctx)

        async def _dispatch():
            match action:
                case "read":
                    return await transaction_manager.read(args["workspace_id"], args["id"])
                case "list":
                    return await transaction_manager.list(
                        args["workspace_id"],
                        args.get("serviceId"),
                        args.get("limit", 50),
                        args.get("offset", 0),
                        service_mock_id=args.get("virtual_service_id"),
                    )
                case "create":
                    return await transaction_manager.create(
                        args["name"], args["workspace_id"], args["serviceId"],
                        args.get("type", "MESSAGING"), args["dsl"], args.get("delay", None),
                        description=args.get("description"),
                        tags=args.get("tags"),
                        priority=args.get("priority"),
                        messaging_transaction_mappings=args.get("messagingTransactionMappings"),
                        sample_body=args.get("sampleBody"),
                    )
                case "update":
                    return await transaction_manager.update(
                        args["id"], args["name"], args["workspace_id"],
                        args.get("type", "MESSAGING"), args["dsl"], args.get("delay", None),
                        description=args.get("description"),
                        tags=args.get("tags"),
                        priority=args.get("priority"),
                        messaging_transaction_mappings=args.get("messagingTransactionMappings"),
                        sample_body=args.get("sampleBody"),
                    )
                case "validate_template":
                    return await transaction_manager.validate_template(args["template"])
                case "convert_template":
                    return await transaction_manager.convert_template(args["template"])
                case "assign_keystore":
                    return await transaction_manager.assign_asset(
                        args["id"], args["workspace_id"],
                        "CLIENT_KEYSTORE_TRUSTSTORE", args["asset_id"], args["alias"],
                    )
                case "assign_certificate":
                    return await transaction_manager.assign_asset(
                        args["id"], args["workspace_id"],
                        "CLIENT_TRUSTSTORE_CERT", args["asset_id"], None,
                    )
                case _:
                    return BaseResult(error=f"Action {action} not found in transaction manager tool")

        try:
            return await run_tool("virtual_services_messaging_transaction", action, ctx, _dispatch)
        except Exception as exc:
            return error_result(exc)
