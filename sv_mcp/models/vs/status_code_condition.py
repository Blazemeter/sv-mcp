from typing import Optional

from pydantic import BaseModel, Field

from sv_mcp.models.vs.matcher_dsl import MatcherDsl


class StatusCodeCondition(BaseModel):
    status: int = Field(200, description="Status code")
    statusMessage: Optional[str] = Field("OK", description="HTTP header name")
    matcher: MatcherDsl = Field(..., description="Condition matcher")

    class Config:
        extra = "allow"  # allows additional unexpected fields
