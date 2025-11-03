from typing import (List, Any, Optional)

from vs_mcp.models.vs.mock_service_transaction import MockServiceTransaction
from vs_mcp.models.vs.virtual_service_template import VirtualServiceTemplate, ActionResult


def format_virtual_service_templates(templates: List[Any], params: Optional[dict] = None) -> List[VirtualServiceTemplate]:
    formatted_vs = []
    for vs in templates:
        formatted_vs.append(
            VirtualServiceTemplate(
                id=vs.get("id"),
                name=vs.get("name"),
                serviceId=vs.get("serviceId"),
                configurationId=vs.get("configurationId", None),
                noMatchingRequestPreference=vs.get("noMatchingRequestPreference"),
                replicas=vs.get("replicas"),
                mockServiceTransactions=[MockServiceTransaction(**d) for d in vs.get("mockServiceTransactions") or []],
                httpRunnerEnabled=vs.get("httpRunnerEnabled"),
            )
        )
    return formatted_vs

