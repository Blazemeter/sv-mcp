from typing import Optional, List

from pydantic import BaseModel, Field

from sv_mcp.models.vs.http_header import HttpHeader
from sv_mcp.models.vs.messaging_property import MessagingProperty
from sv_mcp.models.vs.response_delay import ResponseDelay


class MessagingResponseDsl(BaseModel):
    messageType: Optional[str] = Field(
        None,
        description=(
            "JMS message type of the response. "
            "One of: TEXT_MESSAGE, BYTES_MESSAGE, MAP_MESSAGE, STREAM_MESSAGE, OBJECT_MESSAGE."
        )
    )
    content: Optional[str] = Field(
        "", description="Response body payload. Provide as plain text (e.g. '{\"status\":\"ok\"}') or as a valid base64 string. Plain text and invalid base64 are auto-encoded by the tool."
    )
    charset: Optional[str] = Field(
        "UTF-8", description="Character set for the response content (default UTF-8)"
    )
    failoverEnabled: Optional[bool] = Field(
        None, description="Whether failover is enabled for this response"
    )
    headers: Optional[List[HttpHeader]] = Field(
        [], description="JMS headers of the outgoing message"
    )
    properties: Optional[List[MessagingProperty]] = Field(
        [], description="JMS properties of the outgoing message"
    )
    responseDelay: Optional[ResponseDelay] = Field(
        None, description="Delay configuration applied to this response"
    )

    class Config:
        extra = "allow"
