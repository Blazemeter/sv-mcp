from typing import Optional, List

from pydantic import BaseModel, Field

from sv_mcp.models.vs.http_header import HttpHeader
from sv_mcp.models.vs.messaging_property import MessagingProperty


class RecordedMessage(BaseModel):
    id: Optional[int] = Field(None, description="Unique identifier of the recorded message")
    name: Optional[str] = Field(None, description="Message name")
    messageType: Optional[str] = Field(
        None,
        description=(
            "JMS message type. "
            "One of: TEXT_MESSAGE, BYTES_MESSAGE, MAP_MESSAGE, STREAM_MESSAGE, OBJECT_MESSAGE."
        )
    )
    content: Optional[str] = Field(None, description="Base64-encoded message payload")
    destination: Optional[str] = Field(None, description="Target queue/topic/subscription name")
    destinationType: Optional[str] = Field(
        None, description="Destination type: QUEUE, TOPIC, or SUBSCRIPTION"
    )
    index: Optional[int] = Field(
        None, description="Sequence position within the recording (controls playback order)"
    )
    delay: Optional[int] = Field(None, description="Inter-message delay in ms")
    correlationId: Optional[str] = Field(None, description="JMS correlation ID")
    headers: Optional[List[HttpHeader]] = Field([], description="JMS / MQMD headers")
    properties: Optional[List[MessagingProperty]] = Field([], description="JMS properties")
    recordedAt: Optional[str] = Field(None, description="ISO-8601 timestamp when message was recorded")

    class Config:
        extra = "ignore"
