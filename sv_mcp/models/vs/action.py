from typing import Optional, List

from pydantic import BaseModel, Field

from sv_mcp.models.vs.assigned_asset import AssignedAsset
from sv_mcp.models.vs.web_action import WebAction


class Action(BaseModel):
    id: int = Field(..., description="Action identifier")
    name: str = Field(..., description="Action name")
    actionType: str = Field(..., description="Action type")
    definition: WebAction = Field(..., description="Action definition")
    assets: Optional[List[AssignedAsset]] = Field(None, description="List of assets")

    class Config:
        extra = "ignore"  # ignore any additional fields in input dicts
