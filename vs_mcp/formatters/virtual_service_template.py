from typing import (List, Any, Optional)

from vs_mcp.models.vs.assigned_asset import AssignedAsset
from vs_mcp.models.vs.mock_service_transaction import MockServiceTransaction
from vs_mcp.models.vs.virtual_service_template import VirtualServiceTemplate, ActionResult


def format_virtual_service_templates(templates: List[Any], params: Optional[dict] = None) -> List[VirtualServiceTemplate]:
    formatted_vs = []
    for t in templates:
        formatted_vs.append(
            VirtualServiceTemplate(
                id=t.get("id"),
                name=t.get("name"),
                serviceId=t.get("serviceId"),
                configurationId=t.get("configurationId", None),
                noMatchingRequestPreference=t.get("noMatchingRequestPreference"),
                replicas=t.get("replicas"),
                mockServiceTransactions=[MockServiceTransaction(**d) for d in t.get("mockServiceTransactions") or []],
                httpRunnerEnabled=t.get("httpRunnerEnabled"),
                assets=[AssignedAsset(**d) for d in t.get("assets") or []],
            )
        )
    return formatted_vs

