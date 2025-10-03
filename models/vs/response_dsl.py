from typing import Optional, List
from pydantic import BaseModel, Field
from models.vs.http_header import HttpHeader

class ResponseDsl(BaseModel):
    status: int = Field(
        ...,
        description="HTTP status code of the response for the transaction response matching. E.g., 200, 404."
    )
    headers: Optional[List[HttpHeader]] = Field(
        None,
        description="List of response headers"
    )
    content: Optional[str] = Field(
        None,
        description="Base64 encoded body of the response"
    )

    class Config:
        extra = "allow"
