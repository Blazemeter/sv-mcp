from conftest import load_fixture
from sv_mcp.formatters.virtual_service import format_virtual_services, format_virtual_services_action


def test_format_virtual_services_happy_path():
    result = format_virtual_services(load_fixture("virtual_service"))
    assert len(result) == 1
    vs = result[0]
    assert vs.id == 55001
    assert vs.name == "My Virtual Service"
    assert vs.status == "RUNNING"
    assert vs.serviceId == 341611
    assert vs.type == "TRANSACTIONAL"


def test_format_virtual_services_null_proxy_no_crash():
    result = format_virtual_services(load_fixture("virtual_service"))
    assert result[0].proxy is None


def test_format_virtual_services_null_broker_config_no_crash():
    result = format_virtual_services(load_fixture("virtual_service"))
    assert result[0].brokerConfig is None


def test_format_virtual_services_mock_transactions_parsed():
    result = format_virtual_services(load_fixture("virtual_service"))
    txns = result[0].mockServiceTransactions
    assert txns is not None
    assert len(txns) == 1
    assert txns[0].txnId == 6485927


def test_format_virtual_services_endpoints_parsed():
    result = format_virtual_services(load_fixture("virtual_service"))
    endpoints = result[0].endpoints
    assert endpoints is not None
    assert len(endpoints) == 1
    assert endpoints[0].endpoint == "http://vs.blazemeter.com:8080"


def test_format_virtual_services_empty_assets():
    result = format_virtual_services(load_fixture("virtual_service"))
    assert result[0].assets == []


def test_format_virtual_services_empty_list():
    assert format_virtual_services([]) == []


def test_format_virtual_services_action():
    raw = [{"trackingId": "uuid-track-001"}]
    result = format_virtual_services_action(raw)
    assert len(result) == 1
    assert result[0].tracking_id == "uuid-track-001"
