from typing import (List, Any, Optional)

from sv_mcp.models.vs.service import Service


def format_services(services: List[Any], params: Optional[dict] = None) -> List[Service]:
    formatted_services = []
    for service in services:
        formatted_services.append(
            Service(
                id=service.get("id"),
                name=service.get("name", "Unknown")
            )
        )
    return formatted_services
