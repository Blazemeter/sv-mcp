from conftest import load_fixture
from sv_mcp.formatters.service import format_services


def test_format_services_happy_path():
    result = format_services(load_fixture("service"))
    assert len(result) == 1
    assert result[0].id == 341611
    assert result[0].name == "sort verify"


def test_format_services_missing_name_uses_unknown():
    result = format_services([{"id": 1}])
    assert result[0].name == "Unknown"


def test_format_services_empty_list():
    assert format_services([]) == []
