import base64
from typing import Optional, Dict, Any, Annotated

import httpx
from mcp.server.fastmcp import Context

from sv_mcp.config.blazemeter import VS_TRANSACTIONS_ENDPOINT, WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX, \
    VS_VALIDATIONS_ENDPOINT, \
    VS_CONVERT_ENDPOINT
from sv_mcp.config.token import BzmToken
from sv_mcp.formatters.transaction import format_http_transactions
from sv_mcp.formatters.validations import format_validation_request
from sv_mcp.models.result import BaseResult
from sv_mcp.models.vs.generic_dsl import GenericDsl
from sv_mcp.models.vs.http_transaction import HttpTransaction
from sv_mcp.models.vs.matching_log_entry import MatchingLogEntry
from sv_mcp.models.vs.sandbox_response import SandboxResponse
from sv_mcp.telemetry import run_tool
from sv_mcp.tools.utils import vs_api_request, error_result
from sv_mcp.tools.vs.sandbox_manager import SandboxManager


class HttpTransactionManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def read(self, workspace_id: int, transaction_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{transaction_id}",
            result_formatter=format_http_transactions
        )

    async def list(self, workspace_id: int, service_id: int, limit: int = 50, offset: int = 0) -> BaseResult:
        parameters = {
            "limit": limit,
            "skip": offset,
            "type": "HTTP"
        }
        if service_id is not None:
            parameters["serviceId"] = service_id
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}",
            result_formatter=format_http_transactions,
            params=parameters)

    async def create(self, transaction_name: str, workspace_id: int, service_id,
                     dsl: GenericDsl, delay: int) -> BaseResult:
        # Convert GenericDsl to dict for JSON serialization
        dsl_dict = dsl.model_dump() if isinstance(dsl, GenericDsl) else dsl
        request = dsl_dict.get("requestDsl")
        if request:
            if request.get("url") is not None:
                request["url"]["key"] = "url"
            body_list = request.get("body", [])
            for body_matcher in body_list:
                value = body_matcher.get("matchingValue")
                if value is not None:
                    body_matcher["matchingValue"] = HttpTransactionManager.to_base64(value)
        if delay:
            response = dsl_dict.get("responseDsl")
            if response:
                response["responseDelay"] = {
                    "type": "FIXED",
                    "duration": delay
                }
        transaction_body = {
            "transactions": [
                {
                    "serviceId": service_id,
                    "type": "HTTP",
                    "dsl": dsl_dict,  # Use the dict version
                    "name": transaction_name,
                }
            ]
        }
        parameters = {
            "serviceId": service_id,
        }
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}",
            result_formatter=format_http_transactions,
            json=transaction_body,
            params=parameters
        )

    async def update(self, id: int, transaction_name: str, workspace_id: int,
                     dsl: GenericDsl, delay: int) -> BaseResult:
        # Convert GenericDsl to dict for JSON serialization
        dsl_dict = dsl.model_dump() if isinstance(dsl, GenericDsl) else dsl
        request = dsl_dict.get("requestDsl")
        if request:
            if request.get("url") is not None:
                request["url"]["key"] = "url"
            body_list = request.get("body", [])
            for body_matcher in body_list:
                value = body_matcher.get("matchingValue")
                if value is not None:
                    body_matcher["matchingValue"] = HttpTransactionManager.to_base64(value)
        if delay:
            response = dsl_dict.get("responseDsl")
            if response:
                response["responseDelay"] = {
                    "type": "FIXED",
                    "duration": delay
                }
        transaction_body = {
            "id": id,
            "type": "HTTP",
            "dsl": dsl_dict,
            "name": transaction_name
        }
        return await vs_api_request(
            self.token,
            "PUT",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{id}",
            result_formatter=format_http_transactions,
            json=transaction_body
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
            result_formatter=format_http_transactions,
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

    async def create_and_test(self, transaction_name: str, workspace_id: int, service_id: int,
                              dsl, delay, test_cases: list) -> BaseResult:
        create_result = await self.create(transaction_name, workspace_id, service_id, dsl, delay)
        if create_result.error:
            return create_result

        transaction_id = create_result.result[0].id if create_result.result else None
        if not transaction_id:
            return BaseResult(error="Transaction was created but ID could not be retrieved")

        sandbox_manager = SandboxManager(self.token, self.ctx)
        init_result = await sandbox_manager.init(workspace_id, transaction_id)
        if init_result.error:
            return BaseResult(
                error=init_result.error,
                info=[f"transaction_id={transaction_id}", "Sandbox init failed — transaction was created"]
            )

        test_results = []
        passed = 0
        for test_case in test_cases:
            test_result = await sandbox_manager.test_request(test_case, workspace_id)
            if test_result.error:
                test_results.append(SandboxResponse(
                    status=0, statusMessage="Error",
                    matchingLog=[MatchingLogEntry(t=0, m=test_result.error)]
                ))
            else:
                if test_result.result:
                    response = test_result.result[0]
                    test_results.append(response)
                    if response.matched:
                        passed += 1
                else:
                    test_results.append(SandboxResponse(
                        status=0, statusMessage="Empty response",
                        matchingLog=[MatchingLogEntry(t=0, m="test_request returned empty result")]
                    ))

        total = len(test_cases)
        failed = total - passed
        info = [f"transaction_id={transaction_id}", f"tests_passed={passed}", f"tests_total={total}"]

        if failed == 0:
            return BaseResult(result=test_results, info=info)
        elif passed == 0:
            return BaseResult(
                result=test_results,
                error=f"All {total} test case(s) failed. Check mismatch_reasons in each result "
                      f"and fix the DSL using the update action.",
                info=info
            )
        else:
            return BaseResult(
                result=test_results,
                warning=[f"{failed} of {total} test case(s) failed. Check mismatch_reasons in failing results."],
                info=info
            )

    def to_base64(input_str: str) -> str:
        encoded_bytes = base64.b64encode(input_str.encode('utf-8'))
        encoded_str = encoded_bytes.decode('utf-8')
        return encoded_str


def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{VS_TOOLS_PREFIX}_http_transaction",
        description="""
        Operations on HTTP transactions. 
        Use this when a user needs to create or select a HTTP transaction.
        DSL type field is mandatory and must be set to "HTTP".
      1. General Rules:
            - If redirect url is required in transaction creation or update, provide it as a redirectUrl field in dsl,
            not as a matcher.
            - Assign intermediate values with {{#assign "varName"}}{{value}}{{/assign}}.
            - Keep JSON objects outside helper calls; helpers should only produce values.
            - Do not nest helpers more than 1–2 levels deep.
            - Each helper must have exactly one opening and one closing brace; do not add extra # or braces.
            - Use handlebars helpers supported by wiremock, specified in https://wiremock.org/docs/response-templating/
            - Use validate_template and convert_template actions to validate and convert templates before using them in transaction definition.
            - Dataset variables (from virtual_services_test_data) are referenced with ${fieldName} syntax, NOT Handlebars.
              Matcher name rules — MUST follow exactly:
                * URL path with ${fieldName}: matcherName MUST be "equals_url". NEVER use "matches_url" with variables.
                * Headers / query params / cookies: matcherName must be "equals" or "equals_insensitive" only.
                  "contains", "matches", "not_matches" do NOT work with dataset variables.
                * Body plain text: matcherName "equals"
                * Body JSON: matcherName "equals_json" (embed as value e.g. {"id": "${id}"})
                  or "matches_json" with equalTo() e.g. [[$.field, equalTo(${id})]]
                * Body XML: matcherName "equals_xml" or "matches_xml" with matching() helper
                * Response content: base64-encode the string containing ${fieldName} — resolves at runtime.
              Extra rules:
                * Same variable used multiple times (path + header + body) must match the SAME value in the request.
                * Undefined variables are treated as literal strings — request must contain the exact text "${varName}".
            - IMPORTANT: When a transaction DSL contains Handlebars templates, always use
              create_and_test instead of create. A transaction is only complete when sandbox
              returns matched=true for all test cases. If matched=false, read mismatch_reasons,
              fix the DSL with update, re-init with virtual_services_sandbox init, then re-test with virtual_services_sandbox test_request.
        Actions:
        - read: Read an HTTP Transaction. Get the information of a transaction.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list transactions from.
                id (int): Mandatory. The id of the transaction to get information.
        - list: List all HTTP transactions. 
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list transactions from.
                serviceId (int): Optional. The id of the service to list transactions from. Without this it will list all transactions in the workspace.
                virtual_service_id (int): Optional. The id of the virtual service to list transactions from. Without this it will list all transactions in the workspace.
                limit (int, default=10, valid=[1 to 50]): The number of transactions to list.
                offset (int, default=0): Number of transactions to skip.
        - validate_template: Validate template. Validates template used in transaction definition.
            args:
                template (str): Mandatory. The handlebars template to validate.
        - convert_template: Convert template. Converts template to blazemeter format.
            args:
                template (str): Mandatory. The handlebars template to validate.
                encode (bool, default=True): Whether to encode the converted template to Base64.
        - create_and_test: Create a new HTTP transaction and immediately validate it in sandbox.
            Use this instead of `create` when the DSL contains Handlebars templates.
            A transaction is only complete when sandbox returns matched=true for all test cases.
            On all-fail: error contains the failure summary; transaction still exists — use update to fix the DSL,
            then re-init with virtual_services_sandbox init and re-test with virtual_services_sandbox test_request.
            On partial fail: warning lists failures; transaction still exists.
            args:
                name (str): Mandatory. The name of the transaction.
                serviceId (int): Mandatory. The id of the service.
                dsl (GenericDsl): Mandatory. The DSL definition.
                workspace_id (int): Mandatory. The id of the workspace.
                delay (int): Optional. Response delay in milliseconds.
                test_cases (list[SandboxRequest]): Mandatory. At least one test request.
                    Each entry has: method (str), path (str), name (str),
                    queryParameters (list, optional), headers (list, optional), content (str base64, optional).
            Returns:
                info: ["transaction_id=<id>", "tests_passed=<n>", "tests_total=<n>"]
                result: List of SandboxResponse per test case.
                result[].matched: True if the test request matched the transaction.
                result[].body: Decoded response body (plain text or JSON).
                result[].mismatch_reasons: Why the request did not match (when matched=False).
                error: All test cases failed, or creation/sandbox init failed.
                    On sandbox init failure, info still contains transaction_id so the transaction can be recovered.
                warning: Some (not all) test cases failed.
        - create: Create a new HTTP transaction.
            Important: before using template in transaction definition validate it and 
            convert it first using validate_template and convert_template actions.
            args(Transaction): A Transaction object with the following fields:
                name (str): Mandatory. The name of the transaction.
                serviceId (int): Mandatory. The id of the service to create the transaction in.
                dsl (GenericDsl): Mandatory. The DSL definition of the transaction.
                workspace_id (int): Mandatory. The id of the workspace.
                delay (int): Optional. Response delay in milliseconds.
        - update: Updates a certain transaction.
            Important: before using template in transaction definition validate it and  
            convert it first using validate_template and convert_template actions.
            args(Transaction): A Transaction object with the following fields:
                id (int): Mandatory. The id of the transaction.
                name (str): Mandatory. The new name of the transaction.
                dsl (GenericDsl): Mandatory. The DSL definition of the transaction.
                workspace_id (int): Mandatory. The id of the workspace. 
                delay (int): Optional. Response delay in milliseconds.
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

        Transaction Schema (including full GenericDsl with RequestDsl and ResponseDsl):
        """ + str(HttpTransaction.model_json_schema())
    )
    async def transaction(
            action: str,
            args: Annotated[Dict[str, Any], HttpTransaction.model_json_schema()],
            ctx: Context
    ) -> BaseResult:
        transaction_manager = HttpTransactionManager(token, ctx)

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
                    )
                case "create":
                    return await transaction_manager.create(
                        args["name"], args["workspace_id"], args["serviceId"],
                        args["dsl"], args.get("delay", None),
                    )
                case "update":
                    return await transaction_manager.update(
                        args["id"], args["name"], args["workspace_id"],
                        args["dsl"], args.get("delay", None),
                    )
                case "validate_template":
                    return await transaction_manager.validate_template(args["template"])
                case "convert_template":
                    return await transaction_manager.convert_template(args["template"])
                case "create_and_test":
                    return await transaction_manager.create_and_test(
                        args["name"], args["workspace_id"], args["serviceId"],
                        args["dsl"], args.get("delay", None), args["test_cases"],
                    )
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
            return await run_tool("virtual_services_http_transaction", action, ctx, _dispatch)
        except Exception as exc:
            return error_result(exc)
