import base64
import traceback
from typing import Optional, Annotated, Dict, Any, List

import httpx
from mcp.server.fastmcp import Context

from vs_mcp.config.blazemeter import VS_ENDPOINT, WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX
from vs_mcp.config.token import BzmToken
from vs_mcp.formatters.virtual_service import format_virtual_services, format_virtual_services_action
from vs_mcp.models.result import BaseResult
from vs_mcp.models.vs.mock_service_transaction import MockServiceTransaction
from vs_mcp.models.vs.virtual_service import VirtualService, ActionResult
from vs_mcp.tools.utils import vs_api_request


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

    async def list(self, workspace_id: int, service_id: Optional[int], limit: int = 50, offset: int = 0) -> BaseResult:
        params = {"limit": limit, "skip": offset}
        if service_id is not None:
            params["serviceId"] = service_id
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}",
            result_formatter=format_virtual_services,
            params=params
        )

    async def create(
            self,
            workspace_id: int,
            vs_name: str,
            service_id: int,
            harborId: str,
            shipId: str,
            replicas: int,
            noMatchingRequestPreference: str,
            endpointPreference: str,
            mock_service_transactions: List[MockServiceTransaction],
            http_runner_enabled: bool
    ) -> BaseResult:
        transactions_list = (
            [txn.model_dump() for txn in mock_service_transactions]
            if isinstance(mock_service_transactions, list)
               and mock_service_transactions
               and isinstance(mock_service_transactions[0], MockServiceTransaction)
            else mock_service_transactions
        )

        vs_body = {
            "name": vs_name,
            "serviceId": service_id,
            "type": "TRANSACTIONAL",
            "harborId": harborId,
            "shipId": shipId,
            "replicas": replicas,
            "mockServiceTransactions": transactions_list,
            "noMatchingRequestPreference": noMatchingRequestPreference,
            "endpointPreference": endpointPreference,
            "httpRunnerEnabled": http_runner_enabled,
        }

        params = {"serviceId": service_id}
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}",
            result_formatter=format_virtual_services,
            json=vs_body,
            params=params,
        )

    async def update(
            self,
            workspace_id: int,
            vs_id: int,
            vs_name: Optional[str],
            service_id: Optional[int],
            harborId: Optional[str],
            shipId: Optional[str],
            replicas: Optional[int],
            noMatchingRequestPreference: Optional[str],
            endpointPreference: Optional[str],
            mock_service_transactions: Optional[List[MockServiceTransaction]],
            http_runner_enabled: Optional[bool],
    ) -> BaseResult:
        update_request = {"id": vs_id, "workspaceId": workspace_id}

        if vs_name is not None:
            update_request["name"] = vs_name
        if service_id is not None:
            update_request["serviceId"] = service_id
        if harborId is not None:
            update_request["harborId"] = harborId
        if shipId is not None:
            update_request["shipId"] = shipId
        if replicas is not None:
            update_request["replicas"] = replicas
        if noMatchingRequestPreference is not None:
            update_request["noMatchingRequestPreference"] = noMatchingRequestPreference
        if endpointPreference is not None:
            update_request["endpointPreference"] = endpointPreference
        if http_runner_enabled is not None:
            update_request["httpRunnerEnabled"] = http_runner_enabled

        if mock_service_transactions is not None:
            transactions_list = (
                [txn.model_dump() for txn in mock_service_transactions]
                if isinstance(mock_service_transactions, list)
                   and mock_service_transactions
                   and isinstance(mock_service_transactions[0], MockServiceTransaction)
                else mock_service_transactions
            )
            update_request["mockServiceTransactions"] = transactions_list

        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services,
            json=update_request,
        )

    async def deploy(self, workspace_id: int, vs_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}/deploy",
            result_formatter=format_virtual_services_action,
        )

    async def stop(self, workspace_id: int, vs_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}/stop",
            result_formatter=format_virtual_services_action,
        )

    async def configure(self, workspace_id: int, vs_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}/configure",
            result_formatter=format_virtual_services_action,
        )

    async def assign_transactions(self, workspace_id: int, vs_id: int, transaction_ids: List[int]) -> BaseResult:
        vs_body = {"includeIds": transaction_ids}
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services,
            json=vs_body,
        )

    async def unassign_transactions(self, workspace_id: int, vs_id: int, transaction_ids: List[int]) -> BaseResult:
        vs_body = {"excludeIds": transaction_ids}
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services,
            json=vs_body,
        )

    async def assign_configuration(self, workspace_id: int, vs_id: int, configuration_id: int) -> BaseResult:
        vs_body = {"configurationId": configuration_id}
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services,
            json=vs_body,
        )

    async def set_proxy(
            self,
            workspace_id: int,
            vs_id: int,
            proxyUrl: str,
            nonProxyHosts: Optional[str],
            username: Optional[str],
            password: Optional[str],
            certificate_id: Optional[int],
    ) -> BaseResult:
        update_request = {"id": vs_id, "workspaceId": workspace_id}
        proxy = {}
        if proxyUrl is not None:
            proxy["proxyUrl"] = proxyUrl
        if nonProxyHosts is not None:
            proxy["nonProxyHosts"] = nonProxyHosts
        if username is not None:
            proxy["username"] = username
        if password is not None:
            proxy["password"] = base64.b64encode(password.encode()).decode()
        if certificate_id is not None:
            assets = []
            assets.append({"assetId": certificate_id, "assetUsageType": "CLIENT_TRUSTSTORE_CERT", "alias": None})
            proxy["assets"] = assets
        update_request["proxy"] = proxy
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services,
            json=update_request,
        )

    async def unset_proxy(
            self,
            workspace_id: int,
            vs_id: int,
    ) -> BaseResult:
        update_request = {"id": vs_id, "workspaceId": workspace_id, "proxy": None}
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services,
            json=update_request,
        )

    async def apply_template(self, workspace_id: int, vs_id: int, template_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}/apply-template/{template_id}",
            result_formatter=format_virtual_services_action
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
                workspace_id (int): Mandatory. The id of the workspace.
                name (str): Mandatory. The name of the virtual service.
                serviceId (int): Mandatory. The id of the service to create the virtual service in.
                harborId (str): Mandatory. The location harbor id. If user not specifies location use '5df144f7d778f066ba4d18d6'
                shipId (str): Mandatory. The location ship id. If user not specifies location use '5df14527665b4a7c76267d44'
                replicas (int): Mandatory. Always set to 1.
                endpointPreference (str): Mandatory. If not specified use 'HTTPS'.
                noMatchingRequestPreference (str): Mandatory. If not specified use 'return404'.
                httpRunnerEnabled: (bool): Mandatory. Must be 'TRUE' for the virtual services of the type 'TRANSACTIONAL'.
        - update: Update an existing new virtual service.
            args(VirtualService): A virtual service object with the following fields:
                workspace_id (int): Mandatory. The id of the workspace.
                vs_id (int): Mandatory. The id of the virtual service.
                name (str): Optional. The name of the virtual service.
                serviceId (int): Optional. The id of the service to create the virtual service in.
                harborId (str): Optional. The location harbor id. If user not specifies location use '5df144f7d778f066ba4d18d6'
                shipId (str): Optional. The location ship id. If user not specifies location use '5df14527665b4a7c76267d44'
                replicas (int): Optional. Always set to 1.
                endpointPreference (str): Optional. If not specified use 'HTTPS'.
                noMatchingRequestPreference (str): Optional. If not specified use 'return404'.
                httpRunnerEnabled: (bool): Optional. Must be 'TRUE' for the virtual services of the type 'TRANSACTIONAL'.
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
        - configure: Configures a virtual service. Only available if Virtual service is running.
            Updates transactions loaded into the virtual service.
            Action result contains tracking id to track the update action. Use tracking tool to track the update action.
            Update action is finished, when tracking status is 'FINISHED'. If update action fails, tracking status is 'FAILED'. 
            args(VirtualService): A virtual service object with the following fields:
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
        - set_proxy: Sets proxy server configuration for the virtual service.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace the virtual service belongs to.
                id (int): Mandatory. The id of the virtual service to set proxy.
                proxyUrl (str): Mandatory. Proxy server address.
                nonProxyHosts (str): Optional. Non-proxy hosts, | separated.
                username (str): Optional. Proxy server username.
                password (str): Optional. Proxy server password.
                certificate_id (int): Optional. The id of the proxy certificate asset if required.
        - unset_proxy: Removes proxy server configuration from the virtual service.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace the virtual service belongs to.
                id (int): Mandatory. The id of the virtual service to remove proxy.     
        - apply_template: Applies virtual service template settings to the virtual service.
            Result contains tracking id to track the update action. Use tracking tool to track the update action.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace the virtual service belongs to.
                id (int): Mandatory. The id of the virtual service to remove proxy.
                template_id (int): Mandatory. The id of the virtual service template.
        VirtualService Schema (including full MockServiceTransaction):
        """ + str(VirtualService.model_json_schema()) + """
        Virtual service deploy/stop/update/delete actions result schema:
        """ + str(ActionResult.model_json_schema())
    )
    async def virtual_service(
            action: str,
            args: Annotated[Dict[str, Any], VirtualService.model_json_schema()],
            ctx: Context,
    ) -> BaseResult:
        vs_manager = VirtualServiceManager(token, ctx)
        try:
            match action:
                case "deploy":
                    return await vs_manager.deploy(args["workspace_id"], args["id"])
                case "stop":
                    return await vs_manager.stop(args["workspace_id"], args["id"])
                case "configure":
                    return await vs_manager.configure(args["workspace_id"], args["id"])
                case "read":
                    return await vs_manager.read(args["workspace_id"], args["id"])
                case "list":
                    return await vs_manager.list(
                        args["workspace_id"],
                        args.get("serviceId"),
                        args.get("limit", 50),
                        args.get("offset", 0),
                    )
                case "create":
                    vs_data = VirtualService(
                        id=args.get("id", 0),
                        name=args["name"],
                        serviceId=args["serviceId"],
                        type="TRANSACTIONAL",
                        harborId=args["harborId"],
                        shipId=args["shipId"],
                        replicas=args.get("replicas", 1),
                        noMatchingRequestPreference=args.get("noMatchingRequestPreference", "return404"),
                        endpointPreference=args.get("endpointPreference", "HTTPS"),
                        mockServiceTransactions=args.get("mockServiceTransactions", []),
                        httpRunnerEnabled=args.get("httpRunnerEnabled", False),
                    )
                    return await vs_manager.create(
                        args["workspace_id"],
                        vs_data.name,
                        vs_data.serviceId,
                        vs_data.harborId,
                        vs_data.shipId,
                        vs_data.replicas,
                        vs_data.noMatchingRequestPreference,
                        vs_data.endpointPreference,
                        vs_data.mockServiceTransactions,
                        vs_data.httpRunnerEnabled,
                    )
                case "update":
                    return await vs_manager.update(
                        args["workspace_id"],
                        args["vs_id"],
                        args.get("name"),
                        args.get("serviceId"),
                        args.get("harborId"),
                        args.get("shipId"),
                        args.get("replicas"),
                        args.get("noMatchingRequestPreference"),
                        args.get("endpointPreference"),
                        args.get("mockServiceTransactions", []),
                        args.get("httpRunnerEnabled"),
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
                case "set_proxy":
                    return await vs_manager.set_proxy(
                        args["workspace_id"], args["id"],
                        args.get("proxyUrl"),
                        args.get("nonProxyHosts"),
                        args.get("username"),
                        args.get("password"),
                        args.get("certificate_id")
                    )
                case "unset_proxy":
                    return await vs_manager.unset_proxy(
                        args["workspace_id"], args["id"]
                    )
                case "apply_template":
                    return await vs_manager.apply_template(
                        args["workspace_id"], args["id"], args["template_id"]
                    )
                case _:
                    return BaseResult(error=f"Action {action} not found in virtual service manager tool")
        except httpx.HTTPStatusError:
            return BaseResult(error=f"Error: {traceback.format_exc()}")
        except Exception:
            return BaseResult(
                error=f"""Error: {traceback.format_exc()}
If you think this is a bug, please contact BlazeMeter support or report issue at https://github.com/BlazeMeter/bzm-mcp/issues"""
            )
