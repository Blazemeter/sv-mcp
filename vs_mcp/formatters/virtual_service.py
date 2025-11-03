from typing import (List, Any, Optional)

from vs_mcp.models.vs.assigned_asset import AssignedAsset
from vs_mcp.models.vs.mock_service_transaction import MockServiceTransaction
from vs_mcp.models.vs.proxy_configuration import ProxyConfiguration
from vs_mcp.models.vs.virtual_service import VirtualService, ActionResult, Endpoint


def format_virtual_services(virtual_services: List[Any], params: Optional[dict] = None) -> List[VirtualService]:
    formatted_vs = []
    for vs in virtual_services:
        formatted_vs.append(
            VirtualService(
                id=vs.get("id"),
                name=vs.get("name"),
                serviceId=vs.get("serviceId"),
                type=vs.get("type"),
                harborId=vs.get("harborId"),
                shipId=vs.get("shipId"),
                configurationId=vs.get("configurationId", None),
                noMatchingRequestPreference=vs.get("noMatchingRequestPreference"),
                endpointPreference=vs.get("endpointPreference"),
                replicas=vs.get("replicas"),
                mockServiceTransactions=[MockServiceTransaction(**d) for d in vs.get("mockServiceTransactions") or []],
                endpoints=[Endpoint(**d) for d in vs.get("endpoints") or []],
                httpRunnerEnabled=vs.get("httpRunnerEnabled"),
                proxy=ProxyConfiguration(**vs.get("proxy")) if vs.get("proxy") else None,
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
