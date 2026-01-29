from typing import List, Any, Optional

from vs_mcp.models.user import User
from vs_mcp.tools.utils import get_date_time_iso


def format_users(users: List[Any], params: Optional[dict] = None) -> List[User]:
    formatted_users = []
    for user in users:
        active_workspace_id = None
        preferences = user.get("preferences", {})
        if preferences and isinstance(preferences, dict):
            active_workspace_id = preferences.get("activeWorkspaceId", None)
        formatted_users.append(
            User(
                user_id=user.get("id"),
                display_name=user.get("displayName"),
                first_name=user.get('firstName'),
                last_name=user.get('lastName'),
                email=user.get("email"),
                access=get_date_time_iso(user.get("access")),
                login=get_date_time_iso(user.get("login")),
                created=get_date_time_iso(user.get("created")),
                updated=get_date_time_iso(user.get("updated")),
                time_zone=user.get("timezone", 0),
                enabled=user.get("enabled"),
                default_project_id=user.get("defaultProjectId"),
                active_workspace_id=active_workspace_id,
            )
        )
    return formatted_users
