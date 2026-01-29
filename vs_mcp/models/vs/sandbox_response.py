from typing import Optional, List

from pydantic import BaseModel, Field

from vs_mcp.models.vs.http_header import HttpHeader
from vs_mcp.models.vs.matching_log_entry import MatchingLogEntry


class SandboxResponse(BaseModel):
    status: int = Field(
        ...,
        description="HTTP status code of the response for the transaction response matching. E.g., 200, 404."
    )
    statusMessage: str = Field(..., description="HTTP status message of the response")
    headers: Optional[List[HttpHeader]] = Field(
        [],
        description="List of response headers"
    )
    body: Optional[str] = Field(
        None,
        description="Base64 encoded body of the response"
    )
    matchingLog: Optional[List[MatchingLogEntry]] = Field(
        [],
        description="Matching log, used for debugging purposes"
    )

    class Config:
        extra = "ignore"  # ignore any additional fields in input dicts
