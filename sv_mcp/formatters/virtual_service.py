from typing import (List, Any, Optional)

from sv_mcp.models.vs.assigned_asset import AssignedAsset
from sv_mcp.models.vs.broker_configuration import BrokerConfiguration
from sv_mcp.models.vs.mock_service_recording import MockServiceRecording
from sv_mcp.models.vs.mock_service_transaction import MockServiceTransaction
from sv_mcp.models.vs.proxy_configuration import ProxyConfiguration
from sv_mcp.models.vs.recorder_config import RecorderConfig
from sv_mcp.models.vs.replay_config import ReplayConfig
from sv_mcp.models.vs.response_delay import ResponseDelay
from sv_mcp.models.vs.virtual_service import VirtualService, ActionResult, Endpoint


def format_virtual_services(virtual_services: List[Any], params: Optional[dict] = None) -> List[VirtualService]:
    formatted_vs = []
    for vs in virtual_services:
        recorder_cfg = None
        if vs.get("recorderConfig"):
            recorder_cfg = RecorderConfig(**vs["recorderConfig"])

        response_delay = None
        if vs.get("responseDelay"):
            response_delay = ResponseDelay(**vs["responseDelay"])

        mock_recordings = [
            MockServiceRecording(
                recordingId=r["recordingId"],
                runtimeConfig=ReplayConfig(**r["runtimeConfig"]) if r.get("runtimeConfig") else None,
            )
            for r in (vs.get("mockServiceRecordings") or [])
        ]

        formatted_vs.append(
            VirtualService(
                id=vs.get("id"),
                name=vs.get("name"),
                status=vs.get("status"),
                serviceId=vs.get("serviceId"),
                type=vs.get("type"),
                harborId=vs.get("harborId"),
                shipId=vs.get("shipId"),
                configurationId=vs.get("configurationId", None),
                noMatchingRequestPreference=vs.get("noMatchingRequestPreference"),
                endpointPreference=vs.get("endpointPreference"),
                replicas=vs.get("replicas"),
                mockServiceTransactions=[MockServiceTransaction(**d) for d in vs.get("mockServiceTransactions") or []],
                mockServiceRecordings=mock_recordings,
                endpoints=[Endpoint(**d) for d in vs.get("endpoints") or []],
                httpRunnerEnabled=vs.get("httpRunnerEnabled"),
                messagingRunnerEnabled=vs.get("messagingRunnerEnabled"),
                messagingProtocol=vs.get("messagingProtocol"),
                priorityMode=vs.get("priorityMode"),
                responseDelay=response_delay,
                recorderConfig=recorder_cfg,
                classPathJars=vs.get("classPathJars"),
                proxy=ProxyConfiguration(**vs.get("proxy")) if vs.get("proxy") else None,
                brokerConfig=BrokerConfiguration(**vs.get("brokerConfig")) if vs.get("brokerConfig") else None,
                assets=[AssignedAsset(**d) for d in vs.get("assets") or []],
            )
        )
    return formatted_vs


def format_virtual_services_action(trackings: List[Any], params: Optional[dict] = None) -> List[ActionResult]:
    action_trackings = []
    for tracking in trackings:
        action_trackings.append(
            ActionResult(
                tracking_id=tracking.get("trackingId")
            )
        )
    return action_trackings
