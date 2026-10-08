from typing import List, Any, Optional

from sv_mcp.models.vs.service_data import ServiceData, ServiceDataLinks


def format_service_data(items: List[Any], params: Optional[dict] = None) -> List[ServiceData]:
    formatted_data = []
    for item in items:
        links = item.get("blazeDataDetailLinksDto")
        formatted_data.append(
            ServiceData(
                links=ServiceDataLinks(**links) if links else None,
                globalVariables=item.get("globalVariables") or {},
                dataSettings=item.get("dataSettings"),
            )
        )
    return formatted_data
