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


def test_format_http_transactions_null_path():
    fixture = load_fixture("transaction")["http"]
    fixture[0]["dsl"]["requestDsl"]["path"] = None
    result = format_http_transactions(fixture)
    assert result[0].dsl.requestDsl.path is None


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


def test_format_messaging_transactions_response_message_type():
    fixture = load_fixture("transaction")
    fixture["messaging"][0]["dsl"]["responseDsl"]["messageType"] = "BYTES_MESSAGE"
    result = format_messaging_transactions(fixture["messaging"])
    assert result[0].dsl.responseDsl.messageType == "BYTES_MESSAGE"


def test_format_messaging_transactions_response_delay():
    fixture = load_fixture("transaction")
    fixture["messaging"][0]["dsl"]["responseDsl"]["responseDelay"] = {
        "type": "FIXED", "fixedDelay": 150
    }
    result = format_messaging_transactions(fixture["messaging"])
    assert result[0].dsl.responseDsl.responseDelay.fixedDelay == 150


def test_format_messaging_transactions_transaction_mapping():
    from sv_mcp.models.vs.broker_configuration import MessagingTransactionMapping
    fixture = load_fixture("transaction")
    fixture["messaging"][0]["messagingTransactionMappings"] = {
        "sourceName": "ORDER.IN",
        "sourceType": "QUEUE",
        "destinations": [{"destinationName": "ORDER.OUT", "destinationType": "QUEUE"}],
    }
    result = format_messaging_transactions(fixture["messaging"])
    tm = result[0].messagingTransactionMappings
    assert tm.sourceName == "ORDER.IN"
    assert tm.destinations[0].destinationName == "ORDER.OUT"


def test_format_messaging_transactions_tags_and_priority():
    fixture = load_fixture("transaction")
    fixture["messaging"][0]["tags"] = ["billing", "v2"]
    fixture["messaging"][0]["priority"] = 5
    result = format_messaging_transactions(fixture["messaging"])
    assert result[0].tags == ["billing", "v2"]
    assert result[0].priority == 5
