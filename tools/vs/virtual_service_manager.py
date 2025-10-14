import traceback
from typing import Optional, Annotated, Dict, Any, List

import httpx
from mcp.server.fastmcp import Context

from config.blazemeter import VS_ENDPOINT, WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX
from config.token import BzmToken
from formatters.virtual_service import format_virtual_services, format_virtual_services_action
from models.result import BaseResult
from models.vs.mock_service_transaction import MockServiceTransaction
from models.vs.virtual_service import VirtualService, ActionResult
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

    async def create(self, vs_name: str, workspace_id: int, service_id: int, type: str, harborId: str, shipId: str,
                     replicas: int, noMatchingRequestPreference: str, endpointPreference: str,
                     mock_service_transactions: List[MockServiceTransaction], http_runner_enabled: bool) -> BaseResult:
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
            "endpointPreference": endpointPreference,
            "httpRunnerEnabled": http_runner_enabled
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

    async def deploy(self, workspace_id: int, vs_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}/deploy",
            result_formatter=format_virtual_services_action
        )

    async def stop(self, workspace_id: int, vs_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}/stop",
            result_formatter=format_virtual_services_action
        )

    async def update(self, workspace_id: int, vs_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}/configure",
            result_formatter=format_virtual_services_action
        )

    async def delete(self, workspace_id: int, vs_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "DELETE",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}/delete",
            result_formatter=format_virtual_services_action
        )

    async def assign_transactions(self, workspace_id: int, id: int, transaction_ids: List[int]) -> BaseResult:
        vs_body = {
            "includeIds": transaction_ids
        }
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{id}",
            result_formatter=format_virtual_services,
            json=vs_body
        )

    async def unassign_transactions(self, workspace_id: int, id: int, transaction_ids: List[int]) -> BaseResult:
        vs_body = {
            "excludeIds": transaction_ids
        }
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{id}",
            result_formatter=format_virtual_services,
            json=vs_body
        )

    async def assign_configuration(self, workspace_id: int, id: int, configuration_id: int) -> BaseResult:
        vs_body = {
            "configurationId": configuration_id
        }
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{id}",
            result_formatter=format_virtual_services,
            json=vs_body
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
                harborId (str): Mandatory. The location harbor id. If user not specifies location use '5df144f7d778f066ba4d18d6'
                shipId (str): Mandatory. The location ship id. If user not specifies location use '5df14527665b4a7c76267d44'
                replicas (int): Mandatory. Always set to 1.
                endpointPreference (str): Mandatory. If not specified use 'HTTPS'.
                noMatchingRequestPreference (str): Mandatory. If not specified use 'return404'.
                httpRunnerEnabled: (bool): Mandatory. Must be 'TRUE' for the virtual services of the type 'TRANSACTIONAL'.
        - deploy: Deploy a virtual service. Deploys the virtual service to the specified harbor and ship.
            Action result contains tracking id to track the deployment. Use tracking tool to track the deployment.
            Deployment is finished, when tracking status is 'FINISHED'. If deployment fails, tracking status is 'FAILED'. 
            After tracking status is 'FINISHED' or 'FAILED' you can read the virtual service to get the endpoint and return to user.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace the virtual service belongs to.
                id (int): Mandatory. The id of the virtual service to deploy.
        - stop: Stop a virtual service. Stops the virtual service.
            Action result contains tracking id to track the stop action. Use tracking tool to track the stop action.
            Stop action is finished, when tracking status is 'FINISHED'. If stop action fails, tracking status is 'FAILED'. 
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace the virtual service belongs to.
                id (int): Mandatory. The id of the virtual service to stop.
        - update: Update a virtual service. Updates the virtual service with the provided information.
            Action result contains tracking id to track the update action. Use tracking tool to track the update action.
            Update action is finished, when tracking status is 'FINISHED'. If update action fails, tracking status is 'FAILED'. 
            args(VirtualService): A virtual service object with the following fields:
                workspace_id (int): Mandatory. The id of the virtual service.
                id (int): Mandatory. The id of the virtual service to update.
        - delete: Delete a virtual service. Deletes the virtual service.
            Action result contains tracking id to track the delete action. Use tracking tool to track the delete action.
            Delete action is finished, when tracking status is 'FINISHED'. If delete action fails, tracking status is 'FAILED'. 
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the virtual service.
                id (int): Mandatory. The id of the virtual service to update.
        - assign_transactions: Assigns the transactions to the virtual service. Transactions should belong to the same service as the virtual service.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace the virtual service belongs to.
                id (int): Mandatory. The id of the virtual service to assign the transaction to.
                transaction_ids (list[int]): Mandatory. The ids of the transactions to assign to the virtual service.
        - unassign_transactions: Unassigns the transactions from the virtual service.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace the virtual service belongs to.
                id (int): Mandatory. The id of the virtual service to assign the transaction to.
                transaction_ids (list[int]): Mandatory. The ids of the transactions to unassign from the virtual service.
        - assign_configuration: Assigns the configuration to the virtual service. To unassign configuration, assign configuration with id None.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace the virtual service belongs to.
                id (int): Mandatory. The id of the virtual service to assign the transaction to.
                configuration_id (list[int]): Mandatory. The id of the configuration to assign to the virtual service.
        VirtualService Schema (including full MockServiceTransaction):
        """ + str(VirtualService.model_json_schema()) + """
        Virtual service deploy/stop/update/delete actions result schema:
        """ + str(ActionResult.model_json_schema())
    )
    async def virtual_service(
            action: str,
            args: Annotated[Dict[str, Any], VirtualService.model_json_schema()],
            ctx: Context
    ) -> BaseResult:
        vs_manager = VirtualServiceManager(token, ctx)
        try:
            match action:
                case "deploy":
                    return await vs_manager.deploy(args["workspace_id"], args["id"])
                case "stop":
                    return await vs_manager.stop(args["workspace_id"], args["id"])
                case "update":
                    return await vs_manager.update(args["workspace_id"], args["id"])
                case "delete":
                    return await vs_manager.delete(args["workspace_id"], args["id"])
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
                        httpRunnerEnabled=args.get("httpRunnerEnabled", False)
                    )

                    return await vs_manager.create(
                        vs_data.name,
                        args["workspace_id"],
                        vs_data.serviceId,
                        vs_data.type,
                        vs_data.harborId,
                        vs_data.shipId,
                        vs_data.replicas,
                        vs_data.noMatchingRequestPreference,
                        vs_data.endpointPreference,
                        vs_data.mockServiceTransactions,
                        vs_data.httpRunnerEnabled,
                    )
                case "assign_transactions":
                    return await vs_manager.assign_transactions(
                        args["workspace_id"], args["id"], args["transaction_ids"]
                    )
                case "unassign_transactions":
                    return await vs_manager.unassign_transactions(
                        args["workspace_id"], args["id"], args["transaction_ids"]
                    )
                case "assign_configuration":
                    return await vs_manager.assign_configuration(
                        args["workspace_id"], args["id"], args["configuration_id"]
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
