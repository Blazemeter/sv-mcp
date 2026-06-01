from typing import Optional, List

from pydantic import BaseModel, Field

from sv_mcp.models.vs.assigned_asset import AssignedAsset
from sv_mcp.models.vs.broker_configuration import MessagingTransactionMapping
from sv_mcp.models.vs.messaging_dsl import MessagingDsl


class MessagingTransaction(BaseModel):
    id: Optional[int] = Field(None, description="The unique identifier of the transaction")
    name: str = Field(..., description="The name of the transaction")
    serviceId: Optional[int] = Field(
        None, description="The unique identifier of the service where the transaction belongs"
    )
    description: Optional[str] = Field(None, description="Human-readable description")
    tags: Optional[List[str]] = Field([], description="Tags for filtering and organization")
    priority: Optional[int] = Field(
        10, description="Matching priority (1–2147483647, default 10)"
    )
    dsl: MessagingDsl = Field(..., description="Transaction DSL")
    messagingTransactionMappings: Optional[MessagingTransactionMapping] = Field(
        None,
        description=(
            "Binds this transaction to a source queue/topic/subscription and "
            "specifies where responses are sent."
        )
    )
    sampleBody: Optional[str] = Field(
        None, description="Example request body for documentation and testing"
    )
    assets: Optional[List[AssignedAsset]] = Field(None, description="List of assets")

    class Config:
        extra = "ignore"
