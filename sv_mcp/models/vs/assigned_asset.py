from typing import Optional

from pydantic import BaseModel, Field


class AssignedAsset(BaseModel):
    assetId: int = Field(..., description="The identifier of the asset")
    assetUsageType: str = Field(..., description="The usage type of the asset")
    alias: Optional[str] = Field(None, description="The asset certificate alias")

    class Config:
        extra = "ignore"  # ignore any additional fields in input dicts
