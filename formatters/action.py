from typing import (List, Any, Optional)

from models.vs.action import Action


def format_actions(actions: List[Any], params: Optional[dict] = None) -> List[Action]:
    formatted_actions = []
    for action in actions:
        formatted_actions.append(
            Action(
                id=action.get("id"),
                name=action.get("name", "Unknown"),
                assets=action.get("assets", []),
            )
        )
    return formatted_actions
