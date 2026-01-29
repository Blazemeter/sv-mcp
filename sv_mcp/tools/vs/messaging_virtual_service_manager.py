import base64
import traceback
from typing import Optional, Annotated, Dict, Any, List

import httpx
from mcp.server.fastmcp import Context

from sv_mcp.config.blazemeter import VS_ENDPOINT, WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX
from sv_mcp.config.token import BzmToken
from sv_mcp.formatters.virtual_service import format_virtual_services, format_virtual_services_action
from sv_mcp.models.result import BaseResult
from sv_mcp.models.vs.mock_service_transaction import MockServiceTransaction
from sv_mcp.models.vs.virtual_service import VirtualService, ActionResult
from sv_mcp.tools.utils import vs_api_request


class MessagingVirtualServiceManager:

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

    async def create_mq9(
            self,
            workspace_id: int,
            vs_name: str,
            service_id: int,
            harborId: str,
            shipId: str,
            mock_service_transactions: List[MockServiceTransaction],
            mq9_broker_hostname: str,
            mq9_broker_port: int,
            mq9_broker_channel: str,
            mq9_queue_manager: str,
            mq9_queue_username: str,
            mq9_queue_password: str,
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
            "type": "MESSAGING",
            "harborId": harborId,
            "shipId": shipId,
            "replicas": 1,
            "mockServiceTransactions": transactions_list,
            "messagingRunnerEnabled": True,
        }

        broker_config = {
            "brokerType": "IBM_MQ9",
            "hostname": mq9_broker_hostname,
            "port": mq9_broker_port,
            "channel": mq9_broker_channel,
            "queueManager": mq9_queue_manager,
            "username": mq9_queue_username,
            "password": mq9_queue_password,
        }
        vs_body["brokerConfig"] = broker_config

        params = {"serviceId": service_id}
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}",
            result_formatter=format_virtual_services,
            json=vs_body,
            params=params,
        )

    async def update_mq9(
            self,
            workspace_id: int,
            vs_id: int,
            vs_name: Optional[str],
            service_id: Optional[int],
            harborId: Optional[str],
            shipId: Optional[str],
            mock_service_transactions: Optional[List[MockServiceTransaction]],
            mq9_broker_hostname: str,
            mq9_broker_port: int,
            mq9_broker_channel: str,
            mq9_queue_manager: str,
            mq9_queue_username: str,
            mq9_queue_password: str,
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
        update_request["messagingRunnerEnabled"] = True
        broker_config = {
            "brokerType": "IBM_MQ9",
            "hostname": mq9_broker_hostname,
            "port": mq9_broker_port,
            "channel": mq9_broker_channel,
            "queueManager": mq9_queue_manager,
            "username": mq9_queue_username,
            "password": mq9_queue_password,
        }
        update_request["brokerConfig"] = broker_config
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

    async def assign_transactions(self, workspace_id: int, vs_id: int, transaction_ids: List[int],
                                  source_name: str, source_type: str,
                                  destination_name: str, destination_type: str) -> BaseResult:
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

    async def assign_queue(self, id: int, workspace_id: int, queue_name: str) -> BaseResult:
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{id}/assign-queue/{queue_name}",
            result_formatter=format_virtual_services
        )

    async def assign_topic(self, id: int, workspace_id: int, topic_name: str) -> BaseResult:
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{id}/assign-topic/{topic_name}",
            result_formatter=format_virtual_services
        )

    async def assign_flow(self, id: int, workspace_id: int, source_name: str, source_type,
                          destination_name: str, destination_type) -> BaseResult:
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{id}/assign-flow/{topic_name}",
            result_formatter=format_virtual_services
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
        - create-mq9: Create an IBM MQ9 messaging virtual service.
            args(VirtualService): A virtual service object with the following fields:
                workspace_id (int): Mandatory. The id of the workspace.
                name (str): Mandatory. The name of the virtual service.
                serviceId (int): Mandatory. The id of the service to create the virtual service in.
                harborId (str): Mandatory. The location harbor id.
                shipId (str): Mandatory. The location ship id.
                mq9_broker_hostname(str): Mandatory. The hostname of the IBM MQ9 broker.          
                mq9_broker_port(str): Mandatory. The port of the IBM MQ9 broker.          
                mq9_broker_channel(str): Mandatory. The IBM MQ9 channel name.          
                mq9_queue_manager(str): Mandatory. The IBM MQ9 queue manager name.          
                mq9_queue_username(str): Mandatory. The IBM MQ9 broker username.          
                mq9_queue_password(str): Mandatory. The IBM MQ9 broker password.          
        - update-mq9: Update an existing IBM MQ9 virtual service.
            args(VirtualService): A virtual service object with the following fields:
                workspace_id (int): Mandatory. The id of the workspace.
                vs_id (int): Mandatory. The id of the virtual service.
                name (str): Optional. The name of the virtual service.
                serviceId (int): Optional. The id of the service to create the virtual service in.
                harborId (str): Optional. The location harbor id.
                shipId (str): Optional. The location ship id.
                mq9_broker_hostname(str): Optional. The hostname of the IBM MQ9 broker.          
                mq9_broker_port(str): Optional. The port of the IBM MQ9 broker.          
                mq9_broker_channel(str): Optional. The IBM MQ9 channel name.          
                mq9_queue_manager(str): Optional. The IBM MQ9 queue manager name.          
                mq9_queue_username(str): Optional. The IBM MQ9 broker username.          
                mq9_queue_password(str): Optional. The IBM MQ9 broker password.   
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
        - assign_queue: Assign Queue to the Messaging Virtual Service.
            args(dict):
                id (int): Mandatory. The id of the Virtual Service.
                workspace_id (int): Mandatory. The id of the workspace.    
                queue_name (str): Mandatory. The queue name.    
        - assign_topic: Assign Topic to the Messaging Virtual Service.
            args(dict):
                id (int): Mandatory. The id of the Virtual Service.
                workspace_id (int): Mandatory. The id of the workspace.    
                topic_name (str): Mandatory. The topic name.    
                                  
        VirtualService Schema (including full MockServiceTransaction):
        """ + str(VirtualService.model_json_schema()) + """
        Virtual service deploy/stop/update/delete actions result schema:
        """ + str(ActionResult.model_json_schema())
    )
    async def messaging_virtual_service(
            action: str,
            args: Annotated[Dict[str, Any], VirtualService.model_json_schema()],
            ctx: Context,
    ) -> BaseResult:
        vs_manager = MessagingVirtualServiceManager(token, ctx)
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
                case "create-mq9":
                    return await vs_manager.create_mq9(
                        args["workspace_id"],
                        args["name"],
                        args["serviceId"],
                        args["harborId"],
                        args["shipId"],
                        args.get("mockServiceTransactions", []),
                        args.get("mq9_broker_hostname"),
                        args.get("mq9_broker_port"),
                        args.get("mq9_broker_channel"),
                        args.get("mq9_queue_manager"),
                        args.get("mq9_queue_username"),
                        args.get("mq9_queue_password"),
                    )
                case "update-mq9":
                    return await vs_manager.update_mq9(
                        args["workspace_id"],
                        args["vs_id"],
                        args.get("name"),
                        args.get("serviceId"),
                        args.get("harborId"),
                        args.get("shipId"),
                        args.get("mockServiceTransactions", []),
                        args.get("mq9_broker_hostname"),
                        args.get("mq9_broker_port"),
                        args.get("mq9_broker_channel"),
                        args.get("mq9_queue_manager"),
                        args.get("mq9_queue_username"),
                        args.get("mq9_queue_password"),
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
                case "assign_queue":
                    return await vs_manager.assign_queue(
                        args["id"],
                        args["workspace_id"],
                        args["queue_name"],
                    )
                case "assign_topic":
                    return await vs_manager.assign_topic(
                        args["id"],
                        args["workspace_id"],
                        args["topic_name"],
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
