from typing import Optional, List

from pydantic import BaseModel, Field

from models.vs.http_header import HttpHeader
from models.vs.messaging_property import MessagingProperty


class MessagingResponseDsl(BaseModel):
    headers: Optional[List[HttpHeader]] = Field(
        [],
        description="List of the jms headers of the outgoing message"
    )
    properties: Optional[List[MessagingProperty]] = Field(
        [],
        description="Base64 encoded body of the outgoing message"
    )
    content: Optional[str] = Field(
        "",
        description="Base64 encoded body of the outgoing message"
    )
    class Config:
        extra = "allow"
