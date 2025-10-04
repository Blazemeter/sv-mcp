from pydantic import BaseModel, Field


class MockServiceTransaction(BaseModel):
    txnId: int = Field(..., description="Transaction id.")
    priority: int = Field(10, description="Transaction Priority. If not specified, defaults to 10.")

    class Config:
        extra = "ignore"
