from typing import Optional, List

from pydantic import BaseModel, Field, model_validator

from sv_mcp.models.vs.http_header import HttpHeader
from sv_mcp.models.vs.matching_log_entry import MatchingLogEntry


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
        description="Decoded response body (plain text or JSON). Empty when no transaction matched."
    )
    matchingLog: Optional[List[MatchingLogEntry]] = Field(
        [],
        description="Raw matching log entries from WireMock, used for debugging."
    )
    matched: bool = Field(
        False,
        description="True when the request was matched by a transaction (matchingLog is empty). "
                    "False means no transaction matched — check mismatch_reasons."
    )
    mismatch_reasons: List[str] = Field(
        default_factory=list,
        description="Plain-text reasons why the request did not match any transaction. "
                    "Populated from matchingLog when matched=False."
    )

    @model_validator(mode="after")
    def derive_match_fields(self) -> "SandboxResponse":
        log = self.matchingLog or []
        self.matched = len(log) == 0
        reasons = [entry.m for entry in log if entry.m]
        self.mismatch_reasons = reasons if reasons else (["No match details available"] if log else [])
        return self

    class Config:
        extra = "ignore"
