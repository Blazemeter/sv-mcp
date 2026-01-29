import base64
import traceback
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
from sv_mcp.tools.utils import vs_api_request


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
        try:
            match action:
                case "read":
                    return await transaction_manager.read(args["workspace_id"], args["id"])
                case "list":
                    return await transaction_manager.list(
                        args["workspace_id"],
                        args.get("serviceId"),
                        args.get("limit", 50),
                        args.get("offset", 0)
                    )
                case "create":
                    return await transaction_manager.create(
                        args["name"],
                        args["workspace_id"],
                        args["serviceId"],
                        args["dsl"],
                        args.get("delay", None),
                    )
                case "update":
                    return await transaction_manager.update(
                        args["id"],
                        args["name"],
                        args["workspace_id"],
                        args["dsl"],
                        args.get("delay", None),
                    )
                case "validate_template":
                    return await transaction_manager.validate_template(args["template"])
                case "convert_template":
                    return await transaction_manager.convert_template(args["template"])
                case "assign_keystore":
                    return await transaction_manager.assign_asset(
                        args["id"],
                        args["workspace_id"],
                        "CLIENT_KEYSTORE_TRUSTSTORE",
                        args["asset_id"],
                        args["alias"],
                    )
                case "assign_certificate":
                    return await transaction_manager.assign_asset(
                        args["id"],
                        args["workspace_id"],
                        "CLIENT_TRUSTSTORE_CERT",
                        args["asset_id"],
                        None,
                    )
                case _:
                    return BaseResult(
                        error=f"Action {action} not found in transaction manager tool"
                    )
        except httpx.HTTPStatusError:
            return BaseResult(
                error=f"Error: {traceback.format_exc()}"
            )
        except Exception:
            return BaseResult(
                error=f"""Error: {traceback.format_exc()}
                          If you think this is a bug, please contact BlazeMeter support or report issue at https://github.com/BlazeMeter/bzm-mcp/issues"""
            )
