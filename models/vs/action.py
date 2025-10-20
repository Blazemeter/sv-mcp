from typing import Optional, List

from pydantic import BaseModel, Field

from models.vs.assigned_asset import AssignedAsset


class Action(BaseModel):
    id: int = Field(..., description="Action identifier")
    name: str = Field(..., description="Action name")
    assets: Optional[List[AssignedAsset]] = Field(None, description="List of assets")

    class Config:
        extra = "ignore"  # ignore any additional fields in input dicts
