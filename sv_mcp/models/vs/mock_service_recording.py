from typing import Optional
from pydantic import BaseModel, Field

from sv_mcp.models.vs.replay_config import ReplayConfig


class MockServiceRecording(BaseModel):
    recordingId: int = Field(..., description="ID of the recording to include in this virtual service")
    runtimeConfig: Optional[ReplayConfig] = Field(
        None, description="Replay configuration for this recording"
    )

    class Config:
        extra = "ignore"
