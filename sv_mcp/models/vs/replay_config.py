from typing import Optional
from pydantic import BaseModel, Field


class ReplayConfig(BaseModel):
    replayCount: Optional[int] = Field(1, description="Number of times to replay the recording")
    delayBetweenReplays: Optional[int] = Field(0, description="Delay in ms between replays")
    initialDelay: Optional[int] = Field(0, description="Initial delay in ms before the first replay")

    class Config:
        extra = "allow"
