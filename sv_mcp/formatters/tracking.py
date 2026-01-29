from typing import (List, Any, Optional)

from sv_mcp.models.vs.trackings import MasterTracking, MasterTrackingData, FileUploadTrackingData, FileUploadTracking


def format_trackings(trackings: List[Any], params: Optional[dict] = None) -> List[MasterTracking]:
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


def format_asset_trackings(trackings: List[Any], params: Optional[dict] = None) -> List[MasterTracking]:
    formatted_trackings = []
    for tracking in trackings:
        formatted_trackings.append(
            FileUploadTracking(
                trackingId=tracking.get("trackingId"),
                status=tracking.get("status"),
                errors=tracking.get("errors"),
                warnings=tracking.get("warnings"),
                data=FileUploadTrackingData(**tracking.get("data")),
            )
        )
    return formatted_trackings
