from typing import List, Any, Optional

from sv_mcp.models.vs.http_header import HttpHeader
from sv_mcp.models.vs.messaging_property import MessagingProperty
from sv_mcp.models.vs.recorded_message import RecordedMessage
from sv_mcp.models.vs.recording import Recording
from sv_mcp.models.vs.replay_config import ReplayConfig


def format_recordings(recordings: List[Any], params: Optional[dict] = None) -> List[Recording]:
    return [_parse_recording(r) for r in recordings]


def format_recorded_messages(messages: List[Any], params: Optional[dict] = None) -> List[RecordedMessage]:
    return [_parse_recorded_message(m) for m in messages]


def _parse_recording(r: dict) -> Recording:
    return Recording(
        id=r.get("id"),
        name=r.get("name"),
        serviceId=r.get("serviceId"),
        description=r.get("description"),
        tags=r.get("tags") or [],
        messages=[_parse_recorded_message(m) for m in (r.get("messages") or [])],
        runtimeConfig=ReplayConfig(**r["runtimeConfig"]) if r.get("runtimeConfig") else None,
    )


def _parse_recorded_message(m: dict) -> RecordedMessage:
    return RecordedMessage(
        id=m.get("id"),
        name=m.get("name"),
        messageType=m.get("messageType"),
        content=m.get("content"),
        destination=m.get("destination"),
        destinationType=m.get("destinationType"),
        index=m.get("index"),
        delay=m.get("delay"),
        correlationId=m.get("correlationId"),
        headers=[HttpHeader(**h) for h in (m.get("headers") or [])],
        properties=[MessagingProperty(**p) for p in (m.get("properties") or [])],
        recordedAt=m.get("recordedAt"),
    )
