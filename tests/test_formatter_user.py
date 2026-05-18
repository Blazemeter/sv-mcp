from conftest import load_fixture
from sv_mcp.formatters.user import format_users


def test_format_users_happy_path():
    result = format_users(load_fixture("user"))
    assert len(result) == 1
    u = result[0]
    assert u.user_id == 12345
    assert u.email == "test@example.com"
    assert u.first_name == "Test"
    assert u.last_name == "User"
    assert u.enabled is True
    assert u.active_workspace_id == 347880


def test_format_users_empty_list():
    assert format_users([]) == []


def test_format_users_no_preferences_key():
    raw = [{"id": 1, "displayName": "x", "firstName": "x", "lastName": "x",
            "email": "x@x.com", "access": 0, "login": 0, "created": 0,
            "updated": 0, "timezone": 0, "enabled": True, "defaultProjectId": 1}]
    result = format_users(raw)
    assert result[0].active_workspace_id is None


def test_format_users_preferences_none():
    raw = [{"id": 1, "displayName": "x", "firstName": "x", "lastName": "x",
            "email": "x@x.com", "access": 0, "login": 0, "created": 0,
            "updated": 0, "timezone": 0, "enabled": True, "defaultProjectId": 1,
            "preferences": None}]
    result = format_users(raw)
    assert result[0].active_workspace_id is None


def test_format_users_preferences_empty_dict():
    raw = [{"id": 1, "displayName": "x", "firstName": "x", "lastName": "x",
            "email": "x@x.com", "access": 0, "login": 0, "created": 0,
            "updated": 0, "timezone": 0, "enabled": True, "defaultProjectId": 1,
            "preferences": {}}]
    result = format_users(raw)
    assert result[0].active_workspace_id is None


def test_format_users_timestamps_converted_to_iso():
    result = format_users(load_fixture("user"))
    assert "2024" in result[0].created
    assert "T" in result[0].created
