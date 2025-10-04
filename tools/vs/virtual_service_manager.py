import traceback
from typing import Optional, Annotated, Dict, Any, List
import httpx
from mcp.server.fastmcp import Context

from config.blazemeter import VS_ENDPOINT, WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX
from config.token import BzmToken
from formatters.virtual_service import format_virtual_services
from models.result import BaseResult
from models.vs.mock_service_transaction import MockServiceTransaction
from models.vs.virtual_service import VirtualService
from tools.utils import vs_api_request


class VirtualServiceManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def read(self, workspace_id: int, vs_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services
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
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}",
            result_formatter=format_virtual_services,
            params=parameters)

    async def create(self, vs_name: str, workspace_id: int, service_id, type: str, harborId: str, shipId: str,
                     replicas: int, noMatchingRequestPreference: str, endpointPreference: str,
                     mock_service_transactions: List[MockServiceTransaction]) -> BaseResult:
        # Convert list of Transaction objects to list of dicts
        if isinstance(mock_service_transactions, list) and len(mock_service_transactions) > 0 and isinstance(
                mock_service_transactions[0], MockServiceTransaction):
            transactions_list = [txn.model_dump() for txn in mock_service_transactions]
        else:
            transactions_list = mock_service_transactions

        vs_body = {
            "name": vs_name,
            "serviceId": service_id,
            "type": type,
            "harborId": harborId,
            "shipId": shipId,
            "replicas": replicas,
            "mockServiceTransactions": transactions_list,
            "noMatchingRequestPreference": noMatchingRequestPreference,
            "endpointPreference": endpointPreference
        }

        parameters = {
            "serviceId": service_id,
        }
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}",
            result_formatter=format_virtual_services,
            json=vs_body,
            params=parameters
        )


def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{VS_TOOLS_PREFIX}_virtual_service",
        description="""
        Operations on virtual services. 
        Use this when a user needs to create or select a virtual service.
        Actions:
        - read: Read a virtual service. Get the information of a virtual service.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list virtual services from.
                id (int): Mandatory. The id of the virtual service to get information.
        - list: List all virtual services. 
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list transactions from.
                serviceId (int): Optional. The id of the service to list virtual services from. Without this it will list all virtual services in the workspace.
                limit (int, default=10, valid=[1 to 50]): The number of virtual services to list.
                offset (int, default=0): Number of virtual services to skip.
        - create: Create a new virtual service.
            args(VirtualService): A virtual service object with the following fields:
                workspace_id (int): Mandatory. The id of the virtual service.
                name (str): Mandatory. The name of the virtual service.
                serviceId (int): Mandatory. The id of the service to create the virtual service in.
                type (str): Mandatory. The type of the virtual service.
                harborId (str): Mandatory. The blazemeter location harbor id. If user not specifies location use '5df144f7d778f066ba4d18d6'
                shipId (str): Mandatory. The blazemeter location ship id. If user not specifies location use '5df14527665b4a7c76267d44'
                replicas (int): Mandatory. Always set to 1.
                endpointPreference (str): Mandatory. If not specified use 'HTTPS'.
                noMatchingRequestPreference (str): Mandatory. If not specified use 'return404'.

        VirtualService Schema (including full MockServiceTransaction):
        """ + str(VirtualService.model_json_schema())
    )
    async def virtual_service(
            action: str,
            args: Annotated[Dict[str, Any], VirtualService.model_json_schema()],
            ctx: Context
    ) -> BaseResult:
        vs_manager = VirtualServiceManager(token, ctx)
        try:
            match action:
                case "read":
                    return await vs_manager.read(args["workspace_id"], args["id"])
                case "list":
                    return await vs_manager.list(
                        args["workspace_id"],
                        args.get("serviceId"),
                        args.get("limit", 50),
                        args.get("offset", 0)
                    )
                case "create":
                    # Create Transaction object from args
                    vs_data = VirtualService(
                        id=args.get("id", 0),  # Default id for creation
                        name=args["name"],
                        serviceId=args["serviceId"],
                        type=args["type"],
                        harborId=args["harborId"],
                        shipId=args["shipId"],
                        noMatchingRequestPreference=args["noMatchingRequestPreference"],
                        endpointPreference=args["endpointPreference"],
                        mockServiceTransactions=args["mockServiceTransactions"],
                    )

                    return await vs_manager.create(
                        vs_data.name,
                        args["workspace_id"],
                        vs_data.serviceId,
                        vs_data.type,
                        vs_data.harborId,
                        vs_data.shipId,
                        vs_data.noMatchingRequestPreference,
                        vs_data.endpointPreference,
                        vs_data.mockServiceTransactions
                    )
                case _:
                    return BaseResult(
                        error=f"Action {action} not found in virtual service manager tool"
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
