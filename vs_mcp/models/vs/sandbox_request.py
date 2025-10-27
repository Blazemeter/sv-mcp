from typing import Optional, List

from pydantic import BaseModel, Field

from vs_mcp.models.vs.http_header import HttpHeader
from vs_mcp.models.vs.query_parameter import QueryParameter


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
    content: Optional[str] = Field(
        None,
        description="Base64 encoded body of the response"
    )

    class Config:
        extra = "ignore"  # ignore any additional fields in input dicts
