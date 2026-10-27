from typing import (List, Any, Optional)

from pydantic import ValidationError

from sv_mcp.models.vs.action import Action
from sv_mcp.models.vs.assigned_asset import AssignedAsset
from sv_mcp.models.vs.web_action import WebAction


def format_actions(actions: List[Any], params: Optional[dict] = None) -> List[Action]:
    formatted_actions = []
    for action in actions:
        # The STATE_UPDATE definition shape is not published, so it is passed through verbatim.
        definition = action.get("definition")
        if action.get("actionType") != "STATE_UPDATE":
            try:
                definition = WebAction(**(definition or {}))
            except ValidationError:
                pass
        formatted_actions.append(
            Action(
                id=action.get("id"),
                name=action.get("name", "Unknown"),
                actionType=action.get("actionType"),
                definition=definition,
                transactionId=action.get("transactionId"),
                priority=action.get("priority"),
                conditions=action.get("conditions") or [],
                assets=[AssignedAsset(**d) for d in action.get("assets") or []],
            )
        )
    return formatted_actions
