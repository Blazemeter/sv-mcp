from typing import (List, Any, Optional)

from models.vs.service import Service
from models.vs.trackings import MasterTracking, MasterTrackingData


def format_trackings(trackings: List[Any], params: Optional[dict] = None) -> List[Service]:
    formatted_trackings = []
    for tracking in trackings:
        formatted_trackings.append(
            MasterTracking(
                trackingId=tracking.get("trackingId"),
                status=tracking.get("status"),
                errors=tracking.get("errors"),
                warnings=tracking.get("warnings"),
                data=MasterTrackingData(**tracking.get("data")),
            )
        )
    return formatted_trackings
