from pydantic import BaseModel, Field

from models.vs.request_dsl import RequestDsl
from models.vs.response_dsl import ResponseDsl


class GenericDsl(BaseModel):
    request_dsl: RequestDsl = Field("Request DSL for the transaction request matching")
    response_dsl: ResponseDsl = Field("Response DSL for the transaction response matching")
