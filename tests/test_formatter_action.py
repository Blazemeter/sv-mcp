import pytest
from pydantic import ValidationError

from conftest import load_fixture
from sv_mcp.formatters.action import format_actions


def test_format_actions_happy_path():
    result = format_actions(load_fixture("action"))
    assert len(result) == 1
    a = result[0]
    assert a.id == 888
    assert a.name == "Webhook notify"
    assert a.actionType == "WEB_ACTION"
    assert a.definition.urlValue == "https://hooks.example.com/notify"
    assert a.definition.urlMethod == "POST"


def test_format_actions_definition_headers_parsed():
    result = format_actions(load_fixture("action"))
    headers = result[0].definition.headers
    assert headers is not None
    assert len(headers) == 1
    assert headers[0].name == "Content-Type"


def test_format_actions_empty_assets():
    result = format_actions(load_fixture("action"))
    assert result[0].assets == []


def test_format_actions_empty_list():
    assert format_actions([]) == []


def test_format_actions_none_definition_raises_validation_error_not_type_error():
    """Bug fix: None definition must raise ValidationError, not TypeError."""
    raw = [{"id": 1, "name": "x", "actionType": "WEB_ACTION", "definition": None, "assets": []}]
    with pytest.raises(ValidationError):
        format_actions(raw)
