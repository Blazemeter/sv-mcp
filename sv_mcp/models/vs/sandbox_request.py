from typing import Optional, List

from pydantic import BaseModel, Field

from sv_mcp.models.vs.http_header import HttpHeader
from sv_mcp.models.vs.query_parameter import QueryParameter


class SandboxRequest(BaseModel):
    method: str = Field(..., description="The http method")
    path: str = Field(..., description="The request url path")
    name: str = Field(..., description="The name of the service")
    queryParameters: Optional[List[QueryParameter]] = Field(
        [],
        description="List of query parameters"
    )
    headers: Optional[List[HttpHeader]] = Field(
        [],
        description="List of response headers"
    )
    body: Optional[str] = Field(
        None,
        description=(
            "Plain-text request body to send in the sandbox test. Do not base64-encode it "
            "yourself - the tool encodes it automatically before sending it to the backend, "
            "which expects a field named 'body' (not 'content') containing base64."
        )
    )

    class Config:
        extra = "ignore"  # ignore any additional fields in input dicts
