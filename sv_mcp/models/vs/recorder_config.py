from typing import Optional, List
from pydantic import BaseModel, Field


class RecorderMapping(BaseModel):
    inboundDestination: str = Field(..., description="Source destination to record from")
    outboundDestination: str = Field(..., description="Destination to replay captured messages to")
    originType: str = Field(..., description="Origin type: QUEUE, TOPIC, or SUBSCRIPTION")


class RecorderConfig(BaseModel):
    maxMessagesCount: Optional[int] = Field(
        None, description="Maximum number of messages to capture per recording session"
    )
    maxMessagesPerSecondCount: Optional[int] = Field(
        None, description="Rate limit for capturing messages per second"
    )
    mappings: Optional[List[RecorderMapping]] = Field(
        [], description="Inbound/outbound destination mappings for recording"
    )

    class Config:
        extra = "allow"
