from typing import Optional, List

from pydantic import BaseModel, Field

from sv_mcp.models.vs.http_header import HttpHeader
from sv_mcp.models.vs.status_code_condition import StatusCodeCondition


class ResponseDsl(BaseModel):
    status: int = Field(
        ...,
        description="HTTP status code of the response for the transaction response matching. E.g., 200, 404."
    )
    headers: Optional[List[HttpHeader]] = Field(
        [],
        description="List of response headers"
    )
    content: Optional[str] = Field(
        None,
        description="Base64 encoded body of the response"
    )
    statusCodeConditions: Optional[List[StatusCodeCondition]] = Field([],
                                                                      description="Status code conditions for the response")

    class Config:
        extra = "allow"
