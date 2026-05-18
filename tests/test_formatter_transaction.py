from conftest import load_fixture
from sv_mcp.formatters.transaction import format_http_transactions, format_messaging_transactions


def test_format_http_transactions_happy_path():
    result = format_http_transactions(load_fixture("transaction")["http"])
    assert len(result) == 1
    t = result[0]
    assert t.id == 6485927
    assert t.name == "get test"
    assert t.serviceId == 341611


def test_format_http_transactions_dsl_parsed():
    result = format_http_transactions(load_fixture("transaction")["http"])
    dsl = result[0].dsl
    assert dsl.requestDsl.method == "GET"
    assert dsl.requestDsl.path == "/test"
    assert dsl.responseDsl.status == 200
    assert len(dsl.requestDsl.queryParams) == 1
    assert dsl.requestDsl.queryParams[0].matchingValue == "1"


def test_format_http_transactions_empty_assets():
    result = format_http_transactions(load_fixture("transaction")["http"])
    assert result[0].assets == []


def test_format_http_transactions_missing_assets_key():
    fixture = load_fixture("transaction")["http"]
    del fixture[0]["assets"]
    result = format_http_transactions(fixture)
    assert result[0].assets == []


def test_format_http_transactions_empty_list():
    assert format_http_transactions([]) == []


def test_format_messaging_transactions_happy_path():
    result = format_messaging_transactions(load_fixture("transaction")["messaging"])
    assert len(result) == 1
    t = result[0]
    assert t.id == 7001
    assert t.name == "process order"
    assert t.serviceId == 341611


def test_format_messaging_transactions_dsl_parsed():
    result = format_messaging_transactions(load_fixture("transaction")["messaging"])
    dsl = result[0].dsl
    assert len(dsl.requestDsl.properties) == 1
    assert dsl.requestDsl.properties[0].matchingValue == "NEW"


def test_format_messaging_transactions_empty_list():
    assert format_messaging_transactions([]) == []
