from pydantic import BaseModel, Field
from models.vs.request_dsl import RequestDsl
from models.vs.response_dsl import ResponseDsl

class GenericDsl(BaseModel):
    requestDsl: RequestDsl = Field(
        ...,
        description="Request DSL for the transaction request matching"
    )
    responseDsl: ResponseDsl = Field(
        ...,
        description="Response DSL for the transaction response matching"
    )

    class Config:
        extra = "allow"
