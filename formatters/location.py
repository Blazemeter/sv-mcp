from typing import (List, Any, Optional)

from models.vs.location import Location


def format_locations(locations: List[Any], params: Optional[dict] = None) -> List[Location]:
    formatted_locations = []
    for location in locations:
        formatted_locations.append(
            Location(
                harborId=location.get("harborId"),
                shipId=location.get("shipId"),
                shipName=location.get("shipName"),
                kubernetes=location.get("kubernetes"),
                portRange=(
                    location.get("metadata").get("portRange")
                    if location and location.get("metadata")
                    else ""
                )
            )
        )
    return formatted_locations
