from typing import (List, Any, Optional)

from models.vs.action import Action
from models.vs.service import Service


def format_actions(actions: List[Any], params: Optional[dict] = None) -> List[Service]:
    formatted_actions = []
    for action in actions:
        formatted_actions.append(
            Action(
                name=action.get("name", "Unknown")
            )
        )
    return formatted_actions
