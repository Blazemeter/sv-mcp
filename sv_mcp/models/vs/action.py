from typing import Optional, List, Union, Dict, Any, Annotated

from pydantic import BaseModel, Field

from sv_mcp.models.vs.action_condition import ActionCondition
from sv_mcp.models.vs.assigned_asset import AssignedAsset
from sv_mcp.models.vs.web_action import WebAction

# Conditions echoed by the API that don't fit ActionCondition are kept as raw dicts rather than failing the parse
ActionConditionItem = Annotated[Union[ActionCondition, Dict[str, Any]], Field(union_mode="left_to_right")]


class Action(BaseModel):
    id: int = Field(..., description="Action identifier")
    name: str = Field(..., description="Action name")
    actionType: str = Field(..., description="Action type")
    definition: Union[WebAction, Dict[str, Any]] = Field(
        ...,
        union_mode="left_to_right",
        description="Action definition: WebAction for WEBHOOK/HTTP_CALL; raw dict for STATE_UPDATE and other types"
    )
    transactionId: Optional[int] = Field(None, description="Identifier of the transaction the action belongs to")
    priority: Optional[int] = Field(None, description="Execution order of the action within its transaction")
    conditions: Optional[List[ActionConditionItem]] = Field(
        [],
        description=(
            "Conditions gating the action; all of them must be true for the action to run. "
            "A condition that does not fit ActionCondition is returned as a raw dict"
        )
    )
    assets: Optional[List[AssignedAsset]] = Field(None, description="List of assets")

    class Config:
        extra = "ignore"  # ignore any additional fields in input dicts
