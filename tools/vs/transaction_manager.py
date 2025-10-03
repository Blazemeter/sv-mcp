import traceback
from typing import Optional, Dict, Any
import httpx
from mcp.server.fastmcp import Context

from config.blazemeter import VS_TRANSACTIONS_ENDPOINT, WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX
from config.token import BzmToken
from formatters.transaction import format_transactions
from models.result import BaseResult
from tools.utils import vs_api_request


class TransactionManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def read(self, workspace_id: int, transaction_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}/{transaction_id}",
            result_formatter=format_transactions
        )

    async def list(self, workspace_id: int, service_id: int, limit: int = 50, offset: int = 0) -> BaseResult:
        parameters = {
            "limit": limit,
            "skip": offset
        }
        if service_id is not None:
            parameters["serviceId"] = service_id
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}",
            result_formatter=format_transactions,
            params=parameters)

    async def create(self, service_name: str, workspace_id: int) -> BaseResult:
        service_body = {
            "name": service_name,
        }
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TRANSACTIONS_ENDPOINT}",
            result_formatter=format_transactions,
            json=service_body
        )


def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{VS_TOOLS_PREFIX}_transaction",
        description="""
        Operations on transactions. 
        Use this when a user needs to create or select a transaction.
        Actions:
        - read: Read a Transaction. Get the information of a transaction.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list transactions from.
                transaction_id (int): Mandatory. The id of the transaction to get information.
        - list: List all transactions. 
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list transactions from.
                service_id (int): Optional. The id of the service to list transactions from. Without this it will list all transactions in the workspace.
                virtual_service_id (int): Optional. The id of the virtual service to list transactions from. Without this it will list all transactions in the workspace.
                limit (int, default=10, valid=[1 to 50]): The number of transactions to list.
                offset (int, default=0): Number of transactions to skip.
        - create: Create a new transactions.
            args(dict): Dictionary with the following required parameters:
                transaction_name (str): Mandatory. The required name of the service to create.
                workspace_id (int): Mandatory. The id of the workspace to create transactions in.
                service_id (int): Mandatory. The id of the service to create transactions in.
                type (str): Mandatory. The type of the transaction.
                dsl (GenericDsl): Mandatory. The dsl definition of the transaction.
    """
    )
    async def service(action: str, args: Dict[str, Any], ctx: Context) -> BaseResult:
        transaction_manager = TransactionManager(token, ctx)
        try:
            match action:
                case "read":
                    return await transaction_manager.read(args["workspace_id"], args["transaction_id"])
                case "list":
                    return await transaction_manager.list(args["workspace_id"], args.get("service_id"),
                                                          args.get("limit", 50),
                                                          args.get("offset", 0))
                case "create":
                    return await transaction_manager.create(args["service_name"], args["workspace_id"])
                case _:
                    return BaseResult(
                        error=f"Action {action} not found in service manager tool"
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
