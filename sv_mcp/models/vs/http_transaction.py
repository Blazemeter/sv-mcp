from typing import Optional, List

from pydantic import BaseModel, Field

from sv_mcp.models.vs.assigned_asset import AssignedAsset
from sv_mcp.models.vs.generic_dsl import GenericDsl


class HttpTransaction(BaseModel):
    id: int = Field(None, description="The unique identifier of the transaction")
    name: str = Field(..., description="The name of the transaction")
    serviceId: Optional[int] = Field(None,
                                     description="The unique identifier of the service where the transaction belongs")
    dsl: GenericDsl = Field(..., description="Transaction DSL")
    assets: Optional[List[AssignedAsset]] = Field(None, description="List of assets")

    class Config:
        # Matches GenericDsl/RequestDsl/MatcherDsl for consistency. Note: this alone does not
        # prevent an unexpected top-level field from being dropped in the current request/response
        # paths — format_http_transactions() builds this model from an explicit fixed kwarg list
        # (see formatters/transaction.py), and tool args are read from a raw dict, not validated
        # against this model. The actual fix for a top-level sampleBody being dropped is the
        # explicit fallback in HttpTransactionManager, not this Config setting.
        extra = "allow"
