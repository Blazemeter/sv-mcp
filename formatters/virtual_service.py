from typing import (List, Any, Optional)

from models.vs.mock_service_transaction import MockServiceTransaction
from models.vs.virtual_service import VirtualService, ActionResult, Endpoint


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
            )
        )
    return formatted_vs


def format_virtual_services_action(trackings: List[Any], params: Optional[dict] = None) -> List[VirtualService]:
    action_trackings = []
    for tracking in trackings:
        action_trackings.append(
            ActionResult(
                tracking_id=tracking.get("trackingId")
            )
        )
    return action_trackings
