from typing import Optional, List

from pydantic import BaseModel, Field

from vs_mcp.models.vs.broker_configuration import MessagingDestination


class MockServiceTransaction(BaseModel):
    txnId: int = Field(..., description="Transaction id.")
    priority: int = Field(10, description="Transaction Priority. If not specified, defaults to 10.")
    destinations: Optional[List[MessagingDestination]] = Field([], description="List of messaging destinations.")

    class Config:
        extra = "ignore"
