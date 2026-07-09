from conftest import load_fixture
from sv_mcp.formatters.virtual_service_template import format_virtual_service_templates


def test_format_virtual_service_templates_happy_path():
    result = format_virtual_service_templates(load_fixture("virtual_service_template"))
    assert len(result) == 1
    t = result[0]
    assert t.id == 600
    assert t.name == "My Template"
    assert t.serviceId == 341611
    assert t.noMatchingRequestPreference == "return404"
    assert t.httpRunnerEnabled is True


def test_format_virtual_service_templates_transactions_parsed():
    result = format_virtual_service_templates(load_fixture("virtual_service_template"))
    txns = result[0].mockServiceTransactions
    assert txns is not None
    assert len(txns) == 1
    assert txns[0].txnId == 6485927


def test_format_virtual_service_templates_empty_assets():
    result = format_virtual_service_templates(load_fixture("virtual_service_template"))
    assert result[0].assets == []


def test_format_virtual_service_templates_null_configuration_id():
    result = format_virtual_service_templates(load_fixture("virtual_service_template"))
    assert result[0].configurationId is None


def test_format_virtual_service_templates_empty_list():
    assert format_virtual_service_templates([]) == []
