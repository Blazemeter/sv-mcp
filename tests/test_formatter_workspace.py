import pytest
from conftest import load_fixture
from sv_mcp.formatters.workspace import (
    format_workspaces,
    format_workspaces_detailed,
    format_workspaces_locations,
)


def test_format_workspaces_happy_path():
    result = format_workspaces(load_fixture("workspace"))
    assert len(result) == 1
    ws = result[0]
    assert ws.workspace_id == 347880
    assert ws.workspace_name == "Default workspace"
    assert ws.account_id == 12345
    assert ws.enabled is True
    assert ws.created is not None


def test_format_workspaces_empty_list():
    assert format_workspaces([]) == []


def test_format_workspaces_missing_timestamps_no_crash():
    raw = [{"id": 1, "name": "ws", "accountId": 1, "enabled": True}]
    result = format_workspaces(raw)
    assert result[0].created is None
    assert result[0].updated is None


def test_format_workspaces_detailed_happy_path():
    result = format_workspaces_detailed(load_fixture("workspace"))
    ws = result[0]
    assert ws.workspace_id == 347880
    assert ws.users_count == 5
    assert ws.owner == {"id": 1, "name": "Admin"}


def test_format_workspaces_locations_splits_private_public():
    result = format_workspaces_locations(load_fixture("workspace"))
    assert len(result) == 1
    assert result[0]["account_id"] == 12345
    private = result[0]["private"]
    public = result[0]["public"]
    assert len(private) == 1
    assert len(public) == 1
    assert private[0]["location_id"] == "harbor-us-east-1"
    assert public[0]["location_id"] == "us-east-1"


def test_format_workspaces_locations_mock_purpose_returns_locations():
    """Bug fix: purpose='mock' must map to 'serviceMock' for lookup."""
    result = format_workspaces_locations(load_fixture("workspace"), params={"purpose": "mock"})
    locations = result[0]["private"] + result[0]["public"]
    assert len(locations) == 2


def test_format_workspaces_locations_no_params_returns_local():
    result = format_workspaces_locations(load_fixture("workspace"), params=None)
    locations = result[0]["private"] + result[0]["public"]
    assert len(locations) == 2


def test_format_workspaces_locations_limits_mapped():
    result = format_workspaces_locations(load_fixture("workspace"))
    pub = result[0]["public"][0]
    assert pub["limits"]["location_max_concurrency"] == 100
    assert pub["limits"]["location_max_engines"] == 50
