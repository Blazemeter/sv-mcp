from conftest import load_fixture
from sv_mcp.formatters.transaction import format_http_transactions, format_messaging_transactions


def test_format_http_transactions_happy_path():
    result = format_http_transactions(load_fixture("transaction")["http"][:1])
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


def test_format_http_transactions_decodes_body_matcher_matching_value():
    """Backend stores body-matcher matchingValue as base64; formatter must decode for display,
    symmetric with HttpTransactionManager.to_base64() applied on create/update."""
    result = format_http_transactions(load_fixture("transaction")["http"])
    body_matcher = result[1].dsl.requestDsl.body[0]
    assert body_matcher.matchingValue == '{"foo": "bar"}'


def test_format_http_transactions_decodes_body_matcher_sample_body():
    result = format_http_transactions(load_fixture("transaction")["http"])
    body_matcher = result[1].dsl.requestDsl.body[0]
    assert body_matcher.sampleBody == '{"foo": "bar"}'


def test_format_http_transactions_leaves_non_base64_matching_value_unchanged():
    """Non-body matchers (e.g. url/queryParams) are never base64-encoded on the way in,
    so the formatter must not touch their matchingValue."""
    result = format_http_transactions(load_fixture("transaction")["http"])
    assert result[0].dsl.requestDsl.queryParams[0].matchingValue == "1"
    assert result[0].dsl.requestDsl.url.matchingValue == "/test"


def test_format_http_transactions_leaves_non_body_matcher_sample_body_untouched():
    """sampleBody on a non-body matcher (url/header/query) must not be touched by the decode
    loop, which only iterates request.body — same guarantee as matchingValue, for both fields."""
    transaction = {
        "id": 1,
        "name": "t1",
        "serviceId": 1,
        "dsl": {
            "requestDsl": {
                "url": {"key": "url", "matcherName": "equals_url", "matchingValue": "/test",
                         "sampleBody": "not-base64-should-be-untouched"},
                "body": [],
            },
            "responseDsl": {"status": 200},
        },
    }
    result = format_http_transactions([transaction])
    assert result[0].dsl.requestDsl.url.sampleBody == "not-base64-should-be-untouched"


def test_format_http_transactions_round_trip_no_double_encoding():
    """A read result fed straight back into create/update's to_base64() must reproduce the
    original base64 exactly once — not double-encode an already-decoded-then-reencoded value."""
    from sv_mcp.tools.vs.http_transaction_manager import HttpTransactionManager

    result = format_http_transactions(load_fixture("transaction")["http"])
    body_matcher = result[1].dsl.requestDsl.body[0]
    re_encoded = HttpTransactionManager.to_base64(body_matcher.matchingValue)
    assert re_encoded == "eyJmb28iOiAiYmFyIn0="


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


def test_format_messaging_transactions_decodes_body_matcher_matching_value():
    """Backend stores body-matcher matchingValue as base64; formatter must decode for display,
    symmetric with MessagingTransactionManager.to_base64() applied on create/update."""
    result = format_messaging_transactions(load_fixture("transaction")["messaging"])
    body_matcher = result[0].dsl.requestDsl.body[0]
    assert body_matcher.matchingValue == '{"foo": "bar"}'


def test_format_messaging_transactions_decodes_body_matcher_sample_body():
    result = format_messaging_transactions(load_fixture("transaction")["messaging"])
    body_matcher = result[0].dsl.requestDsl.body[0]
    assert body_matcher.sampleBody == '{"foo": "bar"}'


def test_format_messaging_transactions_leaves_non_body_matcher_matching_value_unchanged():
    """Non-body matchers (e.g. properties/headers) are never base64-encoded on the way in,
    so the formatter must not touch their matchingValue."""
    result = format_messaging_transactions(load_fixture("transaction")["messaging"])
    assert result[0].dsl.requestDsl.properties[0].matchingValue == "NEW"


def test_format_messaging_transactions_tags_and_priority():
    fixture = load_fixture("transaction")
    fixture["messaging"][0]["tags"] = ["billing", "v2"]
    fixture["messaging"][0]["priority"] = 5
    result = format_messaging_transactions(fixture["messaging"])
    assert result[0].tags == ["billing", "v2"]
    assert result[0].priority == 5
