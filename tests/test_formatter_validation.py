from conftest import load_fixture
from sv_mcp.formatters.validations import format_validation_request


def test_format_validation_request_valid():
    result = format_validation_request(load_fixture("validation"))
    assert len(result) == 1
    assert result[0].valid is True
    assert result[0].message == "Template is valid"


def test_format_validation_request_invalid():
    raw = [{"valid": False, "message": "Unexpected token at line 3"}]
    result = format_validation_request(raw)
    assert result[0].valid is False
    assert "line 3" in result[0].message


def test_format_validation_request_empty_list():
    assert format_validation_request([]) == []


def test_format_validation_request_missing_message():
    raw = [{"valid": True}]
    result = format_validation_request(raw)
    assert result[0].valid is True
    assert result[0].message is None
