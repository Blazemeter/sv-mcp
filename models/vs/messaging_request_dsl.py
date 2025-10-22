from typing import Optional, List

from pydantic import BaseModel, Field

from models.vs.matcher_dsl import MatcherDsl


class MessagingRequestDsl(BaseModel):
    headers: Optional[List[MatcherDsl]] = Field(
        [],
        description="List of matchers for the jms headers of the incoming message"
    )
    properties: Optional[List[MatcherDsl]] = Field(
        [],
        description="List of matchers for the jms properties of the incoming message"
    )
    body: Optional[List[MatcherDsl]] = Field(
        [],
        description="List of matchers for the jms message body"
    )

    class Config:
        extra = "allow"
