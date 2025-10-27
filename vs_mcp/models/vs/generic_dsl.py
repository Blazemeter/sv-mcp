from typing import Optional

from pydantic import BaseModel, Field

from vs_mcp.models.vs.request_dsl import RequestDsl
from vs_mcp.models.vs.response_dsl import ResponseDsl


class GenericDsl(BaseModel):
    requestDsl: RequestDsl = Field(
        ...,
        description="Request DSL for the transaction request matching"
    )
    responseDsl: ResponseDsl = Field(
        ...,
        description="Response DSL for the transaction response matching"
    )
    redirectUrl: Optional[str] = Field(
        None,
        description="Redirect URL for the transaction"
    )
    type: str = Field("HTTP", description="The type of the transaction. Supported value is 'HTTP'.")
    class Config:
        extra = "allow"
