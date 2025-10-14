from typing import (List, Any, Optional)

from models.vs.configuration import Configuration
from models.vs.service import Service


def format_configurations(configurations: List[Any], params: Optional[dict] = None) -> List[Service]:
    formatted_configurations = []
    for configuration in configurations:
        formatted_configurations.append(
            Configuration(
                id=configuration.get("id", None),
                name=configuration.get("name"),
                description=configuration.get("description", None),
                configurationMap={k: v["value"] for k, v in configuration.get("configurationMap", {}).items()}
            )
        )
    return formatted_configurations
