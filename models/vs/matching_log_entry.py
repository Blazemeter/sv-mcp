from pydantic import BaseModel, Field

class MatchingLogEntry(BaseModel):
    t: int = Field(None, description="Timestamp of when the message was logged (in milliseconds since epoch)")
    m: str = Field(None, description="Log message")

    class Config:
        extra = "allow"  # allows additional unexpected fields
