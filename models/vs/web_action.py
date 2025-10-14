from typing import Optional, List

from pydantic import BaseModel, Field

from models.vs.http_header import HttpHeader
from models.vs.query_parameter import QueryParameter


class WebAction(BaseModel):
    urlValue: str = Field(..., description="Action request url value")
    urlMethod: str = Field(...,
                           description="Action request HTTP method of the request for the transaction request matching. Uppercase, e.g., 'GET', 'POST'")
    bodyContent: Optional[str] = Field(..., description="Action request body content")
    queryParameters: Optional[List[QueryParameter]] = Field(
        [],
        description="List of query parameters"
    )
    headers: Optional[List[HttpHeader]] = Field(
        [],
        description="List of response headers"
    )

    class Config:
        extra = "ignore"  # ignore any additional fields in input dicts
