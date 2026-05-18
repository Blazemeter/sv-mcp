from typing import Optional

from pydantic import BaseModel, Field


class Sandbox(BaseModel):
    userId: Optional[int] = Field(
        None,
        description="User id"
    )
    serviceId: Optional[int] = Field(
        None,
        description="Service id"
    )
    transactionId: Optional[int] = Field(
        None,
        description="Transaction id"
    )

    class Config:
        extra = "ignore"  # ignore any additional fields in input dicts
