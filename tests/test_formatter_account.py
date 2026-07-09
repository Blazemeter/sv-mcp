from conftest import load_fixture
from sv_mcp.formatters.account import format_accounts


def test_format_accounts_happy_path():
    result = format_accounts(load_fixture("account"))
    assert len(result) == 1
    a = result[0]
    assert a.account_id == 12345
    assert a.account_name == "My Account"
    assert a.description == "Test account"
    assert a.ai_consent is True


def test_format_accounts_timestamps_converted():
    result = format_accounts(load_fixture("account"))
    assert "2024" in result[0].created
    assert "T" in result[0].created


def test_format_accounts_missing_name_uses_unknown():
    raw = [{"id": 1, "description": "", "aiConsent": None, "created": 0, "updated": 0}]
    result = format_accounts(raw)
    assert result[0].account_name == "Unknown"


def test_format_accounts_null_ai_consent():
    raw = [{"id": 1, "name": "x", "description": "", "aiConsent": None, "created": 0, "updated": 0}]
    result = format_accounts(raw)
    assert result[0].ai_consent is None


def test_format_accounts_empty_list():
    assert format_accounts([]) == []
