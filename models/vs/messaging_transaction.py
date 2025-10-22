from typing import Optional, List

from pydantic import BaseModel, Field

from models.vs.assigned_asset import AssignedAsset
from models.vs.messaging_dsl import MessagingDsl


class MessagingTransaction(BaseModel):
    id: int = Field(None, description="The unique identifier of the transaction")
    name: str = Field(..., description="The name of the transaction")
    serviceId: Optional[int] = Field(None,
                                     description="The unique identifier of the service where the transaction belongs")
    dsl: MessagingDsl = Field(..., description="Transaction DSL")
    assets: Optional[List[AssignedAsset]] = Field(None, description="List of assets")

    class Config:
        extra = "ignore"
