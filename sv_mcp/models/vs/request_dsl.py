from typing import Optional, List

from pydantic import BaseModel, Field

from sv_mcp.models.vs.matcher_dsl import MatcherDsl


class RequestDsl(BaseModel):
    method: str = Field(
        'GET',
        description="HTTP method of the request for the transaction request matching. Uppercase, e.g., 'GET', 'POST'"
    )
    path: str = Field(
        ...,
        description="Mandatory.Path of the request for the transaction request matching. E.g., '/api/v1/resource'. Used instead of matcher_name for URL matcher definition. Important: Should have same value as url.matchingValue.",
    )
    url: MatcherDsl = Field(
        None,
        description="Mandatory. Matcher definition for the full URL of the request"
    )
    headers: Optional[List[MatcherDsl]] = Field(
        [],
        description="List of matchers for the headers of the request"
    )
    queryParams: Optional[List[MatcherDsl]] = Field(
        [],
        description="List of matchers for the query parameters of the request"
    )
    body: Optional[List[MatcherDsl]] = Field(
        [],
        description="List of matchers for the body of the request"
    )

    class Config:
        extra = "allow"
