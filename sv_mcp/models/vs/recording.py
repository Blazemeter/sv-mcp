from typing import Optional, List

from pydantic import BaseModel, Field

from sv_mcp.models.vs.recorded_message import RecordedMessage
from sv_mcp.models.vs.replay_config import ReplayConfig


class Recording(BaseModel):
    id: Optional[int] = Field(None, description="Unique identifier of the recording")
    name: str = Field(..., description="Recording name")
    serviceId: Optional[int] = Field(
        None, description="ID of the parent service this recording belongs to"
    )
    description: Optional[str] = Field(None, description="Human-readable description")
    tags: Optional[List[str]] = Field([], description="Tags for filtering")
    messages: Optional[List[RecordedMessage]] = Field(
        [], description="Recorded messages (inline on create or fetch with fetchMessages=true)"
    )
    runtimeConfig: Optional[ReplayConfig] = Field(
        None, description="Replay configuration for this recording"
    )

    class Config:
        extra = "ignore"
