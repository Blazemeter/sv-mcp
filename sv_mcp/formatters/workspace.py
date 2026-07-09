from typing import List, Any, Union, Optional

from sv_mcp.models.workspace import WorkspaceDetailed, Workspace
from sv_mcp.tools.utils import get_date_time_iso


def format_workspaces(workspaces: List[Any], params: Optional[dict] = None, detailed: bool = False) -> List[
    Union[WorkspaceDetailed, Workspace]]:
    normalized_workspaces = []
    for workspace in workspaces:
        workspace_element = {
            "workspace_id": workspace.get("id"),
            "workspace_name": workspace.get("name"),
            "account_id": workspace.get("accountId"),
            "created": get_date_time_iso(workspace.get("created")),
            "updated": get_date_time_iso(workspace.get("updated")),
            "enabled": workspace.get("enabled"),
        }
        if detailed:
            workspace_element.update({
                "owner": workspace.get("owner"),
                "allowance": workspace.get("allowance"),
                "users_count": workspace.get("membersCount"),
            })
        workspace_object = WorkspaceDetailed(**workspace_element) if detailed else Workspace(**workspace_element)
        normalized_workspaces.append(workspace_object)
    return normalized_workspaces


def format_workspaces_detailed(workspaces: List[Any], params: Optional[dict] = None) -> List[
    Union[WorkspaceDetailed, Workspace]]:
    return format_workspaces(workspaces=workspaces, params=params, detailed=True)


def format_workspaces_locations(workspaces: List[Any], params: Optional[dict] = None) -> List[Any]:
    purpose_filter = params.get("purpose", "local") if params else None
    purpose_filter_id = purpose_filter
    if purpose_filter and purpose_filter == "mock":
        purpose_filter_id = "serviceMock"
    private_locations = []
    public_locations = []
    account_id = None
    for workspace in workspaces:
        account_id = workspace.get("accountId")
        locations = workspace.get("locations", [])
        for location in locations:
            purposes = location.get("purposes", {})
            if purpose_filter_id in purposes and purposes[purpose_filter_id] or not purpose_filter_id:
                location_element = {
                    "location_id": location["id"],
                    "location_title": location["title"],
                    "limits": {
                        "location_max_concurrency": location["limits"]["concurrency"],
                        "location_max_engines": location["limits"]["engines"],
                        "test_max_duration_in_minutes_per_engine": location["limits"]["duration"],
                        "test_max_concurrency_per_engine": location["limits"]["threadsPerEngine"],
                    }
                }
                if location["id"].startswith("harbor-"):
                    private_locations.append(location_element)
                else:
                    public_locations.append(location_element)
    return [
        {
            "account_id": account_id,
            "private": private_locations,
            "public": public_locations,
        }
    ]
