from typing import (List, Any, Optional)

from vs_mcp.models.vs.action import Action
from vs_mcp.models.vs.assigned_asset import AssignedAsset
from vs_mcp.models.vs.web_action import WebAction


def format_actions(actions: List[Any], params: Optional[dict] = None) -> List[Action]:
    formatted_actions = []
    for action in actions:
        formatted_actions.append(
            Action(
                id=action.get("id"),
                name=action.get("name", "Unknown"),
                actionType=action.get("actionType"),
                definition=WebAction(**action.get("definition")),
                assets=[AssignedAsset(**d) for d in action.get("assets") or []],
            )
        )
    return formatted_actions
