from pydantic import BaseModel, Field

from models.vs.messaging_request_dsl import MessagingRequestDsl
from models.vs.messaging_response_dsl import MessagingResponseDsl


class MessagingDsl(BaseModel):
    requestDsl: MessagingRequestDsl = Field(
        ...,
        description="DSL for the incoming JMS message matching"
    )
    responseDsl: MessagingResponseDsl = Field(
        ...,
        description="DSL for the outgoing JMS message"
    )
    type: str = Field("MESSAGING", description="The type of the transaction. Supported value is 'MESSAGING'.")
    class Config:
        extra = "allow"
