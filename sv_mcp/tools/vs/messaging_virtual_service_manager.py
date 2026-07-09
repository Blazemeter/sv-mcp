from typing import Optional, Annotated, Dict, Any, List

import httpx
from mcp.server.fastmcp import Context

from sv_mcp.config.blazemeter import VS_ENDPOINT, WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX
from sv_mcp.config.token import BzmToken
from sv_mcp.formatters.virtual_service import format_virtual_services, format_virtual_services_action
from sv_mcp.models.result import BaseResult
from sv_mcp.models.vs.mock_service_transaction import MockServiceTransaction
from sv_mcp.models.vs.virtual_service import VirtualService, ActionResult
from sv_mcp.telemetry import run_tool
from sv_mcp.tools.utils import vs_api_request, error_result
from sv_mcp.tools.vs.base_virtual_service_manager import BaseVirtualServiceManager

_PROTOCOL_DESCRIPTIONS = """
Protocol-to-BrokerConfig field matrix:
  IBM_MQ9_JMS / IBM_MQ9_NATIVE: hostname, port (default "1414"), channel, queueManager,
    username, password, sslAuthentication, sslCipherSuite, queues, topics, subscriptions,
    flowConfigurations.
  ACTIVE_MQ_CLASSIC / ACTIVE_MQ_ARTEMIS: hostname, port (default "61616"), username,
    password, embeddedBroker, sslAuthentication, queues, topics, subscriptions,
    flowConfigurations.
  KAFKA: hostname, port (e.g. "broker1:9092,broker2:9092"), username (optional),
    password (optional), autoOffsetReset (earliest|latest|none), numPartitions,
    topics, flowConfigurations.
"""


class MessagingVirtualServiceManager(BaseVirtualServiceManager):

    async def create(
            self,
            workspace_id: int,
            name: str,
            service_id: int,
            harborId: str,
            shipId: str,
            messaging_protocol: str,
            broker_config: dict,
            mock_service_transactions: Optional[List] = None,
            mock_service_recordings: Optional[List] = None,
            recorder_config: Optional[dict] = None,
            priority_mode: Optional[str] = None,
            response_delay: Optional[dict] = None,
            messaging_runner_enabled: bool = True,
    ) -> BaseResult:
        body = {
            "name": name,
            "serviceId": service_id,
            "type": "TRANSACTIONAL",
            "harborId": harborId,
            "shipId": shipId,
            "replicas": 1,
            "messagingProtocol": messaging_protocol,
            "brokerConfig": broker_config,
            "messagingRunnerEnabled": messaging_runner_enabled,
        }
        if mock_service_transactions:
            body["mockServiceTransactions"] = _serialize_transactions(mock_service_transactions)
        if mock_service_recordings:
            body["mockServiceRecordings"] = mock_service_recordings
        if recorder_config is not None:
            body["recorderConfig"] = recorder_config
        if priority_mode is not None:
            body["priorityMode"] = priority_mode
        if response_delay is not None:
            body["responseDelay"] = response_delay

        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}",
            result_formatter=format_virtual_services,
            json=body,
        )

    async def update(
            self,
            workspace_id: int,
            vs_id: int,
            name: Optional[str] = None,
            service_id: Optional[int] = None,
            harborId: Optional[str] = None,
            shipId: Optional[str] = None,
            messaging_protocol: Optional[str] = None,
            broker_config: Optional[dict] = None,
            mock_service_transactions: Optional[List] = None,
            mock_service_recordings: Optional[List] = None,
            recorder_config: Optional[dict] = None,
            priority_mode: Optional[str] = None,
            response_delay: Optional[dict] = None,
            messaging_runner_enabled: Optional[bool] = None,
    ) -> BaseResult:
        body: Dict[str, Any] = {"id": vs_id, "workspaceId": workspace_id}
        if name is not None:
            body["name"] = name
        if service_id is not None:
            body["serviceId"] = service_id
        if harborId is not None:
            body["harborId"] = harborId
        if shipId is not None:
            body["shipId"] = shipId
        if messaging_protocol is not None:
            body["messagingProtocol"] = messaging_protocol
        if broker_config is not None:
            body["brokerConfig"] = broker_config
        if messaging_runner_enabled is not None:
            body["messagingRunnerEnabled"] = messaging_runner_enabled
        if mock_service_transactions is not None:
            body["mockServiceTransactions"] = _serialize_transactions(mock_service_transactions)
        if mock_service_recordings is not None:
            body["mockServiceRecordings"] = mock_service_recordings
        if recorder_config is not None:
            body["recorderConfig"] = recorder_config
        if priority_mode is not None:
            body["priorityMode"] = priority_mode
        if response_delay is not None:
            body["responseDelay"] = response_delay

        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services,
            json=body,
        )

    async def create_mq9(
            self,
            workspace_id: int,
            vs_name: str,
            service_id: int,
            harborId: str,
            shipId: str,
            mock_service_transactions: List,
            mq9_broker_hostname: str,
            mq9_broker_port,
            mq9_broker_channel: str,
            mq9_queue_manager: str,
            mq9_queue_username: str,
            mq9_queue_password: str,
    ) -> BaseResult:
        broker_config = {
            "hostname": mq9_broker_hostname,
            "port": str(mq9_broker_port),
            "channel": mq9_broker_channel,
            "queueManager": mq9_queue_manager,
            "username": mq9_queue_username,
            "password": mq9_queue_password,
        }
        return await self.create(
            workspace_id=workspace_id,
            name=vs_name,
            service_id=service_id,
            harborId=harborId,
            shipId=shipId,
            messaging_protocol="IBM_MQ9_JMS",
            broker_config=broker_config,
            mock_service_transactions=mock_service_transactions,
        )

    async def update_mq9(
            self,
            workspace_id: int,
            vs_id: int,
            vs_name: Optional[str],
            service_id: Optional[int],
            harborId: Optional[str],
            shipId: Optional[str],
            mock_service_transactions: Optional[List],
            mq9_broker_hostname: str,
            mq9_broker_port,
            mq9_broker_channel: str,
            mq9_queue_manager: str,
            mq9_queue_username: str,
            mq9_queue_password: str,
    ) -> BaseResult:
        broker_config = {
            "hostname": mq9_broker_hostname,
            "port": str(mq9_broker_port),
            "channel": mq9_broker_channel,
            "queueManager": mq9_queue_manager,
            "username": mq9_queue_username,
            "password": mq9_queue_password,
        }
        return await self.update(
            workspace_id=workspace_id,
            vs_id=vs_id,
            name=vs_name,
            service_id=service_id,
            harborId=harborId,
            shipId=shipId,
            messaging_protocol="IBM_MQ9_JMS",
            broker_config=broker_config,
            mock_service_transactions=mock_service_transactions,
        )

    async def assign_transactions(
            self,
            workspace_id: int,
            vs_id: int,
            transaction_ids: List[int],
            flow_configuration: Optional[str] = None,
    ) -> BaseResult:
        vs_body: Dict[str, Any] = {"includeIds": transaction_ids}
        if flow_configuration is not None:
            vs_body["flowConfiguration"] = flow_configuration
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services,
            json=vs_body,
        )

    async def assign_recordings(self, workspace_id: int, vs_id: int, recording_ids: List[int]) -> BaseResult:
        vs_body = {"includeRecordingIds": recording_ids}
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services,
            json=vs_body,
        )

    async def unassign_recordings(self, workspace_id: int, vs_id: int, recording_ids: List[int]) -> BaseResult:
        vs_body = {"excludeRecordingIds": recording_ids}
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services,
            json=vs_body,
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


def _serialize_transactions(transactions: List) -> List:
    return (
        [txn.model_dump() for txn in transactions]
        if transactions and isinstance(transactions[0], MockServiceTransaction)
        else transactions
    )


def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{VS_TOOLS_PREFIX}_messaging_virtual_service",
        description="""
        Operations on messaging virtual services.
        Use this when a user needs to create, update, deploy, or manage a messaging virtual service.

        Actions:
        - read: Get full details of a virtual service.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
        - list: List messaging virtual services.
            args:
                workspace_id (int): Mandatory.
                serviceId (int): Optional. Filter by service.
                limit (int, default=10): Max results (1–50).
                offset (int, default=0): Pagination offset.
        - create: Create a messaging virtual service for any supported protocol.
            args:
                workspace_id (int): Mandatory.
                name (str): Mandatory.
                serviceId (int): Mandatory.
                harborId (str): Mandatory. Location harbor ID.
                shipId (str): Mandatory. Location ship ID.
                messagingProtocol (str): Mandatory. One of: IBM_MQ9_JMS, IBM_MQ9_NATIVE,
                    ACTIVE_MQ_CLASSIC, ACTIVE_MQ_ARTEMIS, KAFKA.
                brokerConfig (dict): Mandatory. Protocol-specific connection config.
                """ + _PROTOCOL_DESCRIPTIONS + """
                mockServiceTransactions (list): Optional. Transaction references [{txnId, priority, ...}].
                mockServiceRecordings (list): Optional. Recording references [{recordingId, runtimeConfig}].
                recorderConfig (dict): Optional. Live recording config {maxMessagesCount, maxMessagesPerSecondCount, mappings}.
                priorityMode (str): Optional. DEFAULT or UNIQUE_PRIORITY.
                responseDelay (dict): Optional. {type, fixedDelay} or {type, median, sigma} etc.
                messagingRunnerEnabled (bool): Optional. Default true.
        - update: Update an existing messaging virtual service (partial — only provided fields change).
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
                name (str): Optional.
                serviceId (int): Optional.
                harborId (str): Optional.
                shipId (str): Optional.
                messagingProtocol (str): Optional. Changing protocol requires a new brokerConfig.
                brokerConfig (dict): Optional.
                mockServiceTransactions (list): Optional.
                mockServiceRecordings (list): Optional.
                recorderConfig (dict): Optional.
                priorityMode (str): Optional.
                responseDelay (dict): Optional.
                messagingRunnerEnabled (bool): Optional.
        - create-mq9: (Legacy) Create an IBM MQ9 virtual service using named fields.
            args:
                workspace_id (int): Mandatory.
                name (str): Mandatory.
                serviceId (int): Mandatory.
                harborId (str): Mandatory.
                shipId (str): Mandatory.
                mq9_broker_hostname (str): Mandatory.
                mq9_broker_port (int): Mandatory.
                mq9_broker_channel (str): Mandatory.
                mq9_queue_manager (str): Mandatory.
                mq9_queue_username (str): Mandatory.
                mq9_queue_password (str): Mandatory.
        - update-mq9: (Legacy) Update IBM MQ9 virtual service using named fields.
            args: Same as create-mq9 but all optional except workspace_id and vs_id (int).
        - deploy: Deploy a virtual service.
            Action result contains trackingId. Use tracking tool to poll until FINISHED or FAILED.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
        - stop: Stop a running virtual service.
            Action result contains trackingId.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
        - configure: Hot-reload transactions into a running virtual service.
            Action result contains trackingId.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
        - assign_transactions: Assign transactions to a messaging virtual service.
            When the broker config uses flow configurations, pass flow_configuration so the
            server can copy the named flow's routing (sourceName, sourceType, destinations)
            onto every newly added transaction.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
                transaction_ids (list[int]): Mandatory.
                flow_configuration (str): Optional. Name of a flow in brokerConfig.flowConfigurations[].name.
                    Required when the VS uses flow-based routing — omitting it leaves transactions with
                    an empty MessagingTransactionMapping (no routing).
        - unassign_transactions: Unassign transactions from a virtual service.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
                transaction_ids (list[int]): Mandatory.
        - assign_recordings: Assign recordings to a messaging virtual service.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
                recording_ids (list[int]): Mandatory. IDs of recordings to assign.
        - unassign_recordings: Unassign recordings from a messaging virtual service.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
                recording_ids (list[int]): Mandatory. IDs of recordings to unassign.
        - assign_configuration: Assign a configuration to a virtual service.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
                configuration_id (int): Mandatory. Pass null to unassign.
        - set_proxy: Set proxy configuration.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
                proxyUrl (str): Mandatory.
                nonProxyHosts (str): Optional.
                username (str): Optional.
                password (str): Optional.
                certificate_id (int): Optional.
        - unset_proxy: Remove proxy configuration.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
        - assign_queue: Assign a queue to the virtual service.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
                queue_name (str): Mandatory.
        - assign_topic: Assign a topic to the virtual service.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
                topic_name (str): Mandatory.

        VirtualService schema:
        """ + str(VirtualService.model_json_schema()) + """
        Action result schema:
        """ + str(ActionResult.model_json_schema())
    )
    async def messaging_virtual_service(
            action: str,
            args: Annotated[Dict[str, Any], VirtualService.model_json_schema()],
            ctx: Context,
    ) -> BaseResult:
        vs_manager = MessagingVirtualServiceManager(token, ctx)

        async def _dispatch():
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
                    return await vs_manager.create(
                        workspace_id=args["workspace_id"],
                        name=args["name"],
                        service_id=args["serviceId"],
                        harborId=args["harborId"],
                        shipId=args["shipId"],
                        messaging_protocol=args["messagingProtocol"],
                        broker_config=args["brokerConfig"],
                        mock_service_transactions=args.get("mockServiceTransactions"),
                        mock_service_recordings=args.get("mockServiceRecordings"),
                        recorder_config=args.get("recorderConfig"),
                        priority_mode=args.get("priorityMode"),
                        response_delay=args.get("responseDelay"),
                        messaging_runner_enabled=args.get("messagingRunnerEnabled", True),
                    )
                case "update":
                    return await vs_manager.update(
                        workspace_id=args["workspace_id"],
                        vs_id=args["id"],
                        name=args.get("name"),
                        service_id=args.get("serviceId"),
                        harborId=args.get("harborId"),
                        shipId=args.get("shipId"),
                        messaging_protocol=args.get("messagingProtocol"),
                        broker_config=args.get("brokerConfig"),
                        mock_service_transactions=args.get("mockServiceTransactions"),
                        mock_service_recordings=args.get("mockServiceRecordings"),
                        recorder_config=args.get("recorderConfig"),
                        priority_mode=args.get("priorityMode"),
                        response_delay=args.get("responseDelay"),
                        messaging_runner_enabled=args.get("messagingRunnerEnabled"),
                    )
                case "create-mq9":
                    return await vs_manager.create_mq9(
                        args["workspace_id"],
                        args["name"],
                        args["serviceId"],
                        args["harborId"],
                        args["shipId"],
                        args.get("mockServiceTransactions", []),
                        args["mq9_broker_hostname"],
                        args["mq9_broker_port"],
                        args["mq9_broker_channel"],
                        args["mq9_queue_manager"],
                        args["mq9_queue_username"],
                        args["mq9_queue_password"],
                    )
                case "update-mq9":
                    return await vs_manager.update_mq9(
                        args["workspace_id"],
                        args["id"],
                        args.get("name"),
                        args.get("serviceId"),
                        args.get("harborId"),
                        args.get("shipId"),
                        args.get("mockServiceTransactions"),
                        args.get("mq9_broker_hostname"),
                        args.get("mq9_broker_port"),
                        args.get("mq9_broker_channel"),
                        args.get("mq9_queue_manager"),
                        args.get("mq9_queue_username"),
                        args.get("mq9_queue_password"),
                    )
                case "assign_transactions":
                    return await vs_manager.assign_transactions(
                        args["workspace_id"], args["id"], args["transaction_ids"],
                        flow_configuration=args.get("flow_configuration"),
                    )
                case "unassign_transactions":
                    return await vs_manager.unassign_transactions(
                        args["workspace_id"], args["id"], args["transaction_ids"]
                    )
                case "assign_recordings":
                    return await vs_manager.assign_recordings(
                        args["workspace_id"], args["id"], args["recording_ids"]
                    )
                case "unassign_recordings":
                    return await vs_manager.unassign_recordings(
                        args["workspace_id"], args["id"], args["recording_ids"]
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

        try:
            return await run_tool("virtual_services_messaging_virtual_service", action, ctx, _dispatch)
        except Exception as exc:
            return error_result(exc)
