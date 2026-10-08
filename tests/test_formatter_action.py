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


def test_format_actions_state_update_definition_passed_through():
    raw = load_fixture("action_state_update")
    result = format_actions(raw)
    assert len(result) == 1
    a = result[0]
    assert a.actionType == "STATE_UPDATE"
    assert isinstance(a.definition, dict)
    assert a.definition == raw[0]["definition"]


def test_format_actions_state_update_fields_mapped():
    a = format_actions(load_fixture("action_state_update"))[0]
    assert a.transactionId == 77
    assert a.priority == 2


def test_format_actions_conditions_parsed():
    conditions = format_actions(load_fixture("action_state_update"))[0].conditions
    assert len(conditions) == 1
    assert conditions[0].matcher.key == "${request.query.id}"
    assert conditions[0].matcher.matcherName == "equals"
    assert conditions[0].matcher.matchingValue == "42"


def test_format_actions_unexpected_condition_kept_as_raw_dict():
    """A condition that doesn't fit ActionCondition must not make read/list fail for the whole transaction."""
    raw = load_fixture("action")
    raw[0]["conditions"] = [{"matcher": {"key": "${request.headers.x}", "matcherName": "absent", "matchingValue": None}}]
    conditions = format_actions(raw)[0].conditions
    assert conditions == raw[0]["conditions"]


def test_format_actions_missing_conditions_default_to_empty():
    result = format_actions(load_fixture("action"))
    assert result[0].conditions == []


def test_format_actions_unknown_action_type_keeps_raw_definition():
    raw = [{"id": 1, "name": "a", "actionType": "NEW_TYPE", "definition": {"foo": 1}}]
    assert format_actions(raw)[0].definition == {"foo": 1}


def test_format_actions_keeps_unknown_condition_fields():
    raw = load_fixture("action")
    raw[0]["conditions"] = [{"id": 5, "matcher": {"key": "${request.query.id}", "matcherName": "equals",
                                                   "matchingValue": "42"}}]
    condition = format_actions(raw)[0].conditions[0]
    assert condition.model_dump()["id"] == 5
