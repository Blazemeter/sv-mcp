from pydantic import BaseModel, Field


class Sandbox(BaseModel):
    userId: int = Field(
        ...,
        description="User id"
    )
    serviceId: int = Field(
        ...,
        description="Service id"
    )
    transactionId: int = Field(
        ...,
        description="Transaction id"
    )

    class Config:
        extra = "ignore"  # ignore any additional fields in input dicts
