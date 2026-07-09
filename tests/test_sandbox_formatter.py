from sv_mcp.models.vs.sandbox_response import SandboxResponse
from sv_mcp.formatters.sandbox import format_sandbox_test_request
import base64


def test_sandbox_response_has_matched_field():
    # Empty matchingLog (default) means the request was matched
    r = SandboxResponse(status=200, statusMessage="OK")
    assert r.matched is True


def test_sandbox_response_has_mismatch_reasons_field():
    r = SandboxResponse(status=200, statusMessage="OK")
    assert r.mismatch_reasons == []


def _make_raw(status=200, status_msg="OK", body_text=None, matching_log=None):
    body = base64.b64encode(body_text.encode()).decode() if body_text else None
    return {
        "status": status,
        "statusMessage": status_msg,
        "headers": [],
        "body": body,
        "matchingLog": matching_log or [],
    }


def test_formatter_matched_when_matching_log_empty():
    raw = [_make_raw(body_text='{"key": "value"}')]
    result = format_sandbox_test_request(raw)
    assert result[0].matched is True
    assert result[0].mismatch_reasons == []


def test_formatter_unmatched_when_matching_log_has_entries():
    raw = [_make_raw(
        status=404,
        status_msg="Not Found",
        matching_log=[{"t": 1000, "m": "Request method POST did not match GET"}]
    )]
    result = format_sandbox_test_request(raw)
    assert result[0].matched is False
    assert result[0].mismatch_reasons == ["Request method POST did not match GET"]


def test_formatter_decodes_base64_body():
    raw = [_make_raw(body_text="hello world")]
    result = format_sandbox_test_request(raw)
    assert result[0].body == "hello world"


def test_formatter_none_body_stays_none():
    raw = [_make_raw()]
    result = format_sandbox_test_request(raw)
    assert result[0].body is None


def test_formatter_multiple_mismatch_reasons():
    raw = [_make_raw(
        matching_log=[
            {"t": 1000, "m": "Method mismatch"},
            {"t": 1001, "m": "Path mismatch"},
        ]
    )]
    result = format_sandbox_test_request(raw)
    assert result[0].mismatch_reasons == ["Method mismatch", "Path mismatch"]


def test_formatter_matched_when_matching_log_has_only_success_entries():
    raw = [_make_raw(
        body_text='{"id": 1}',
        matching_log=[
            {"t": 1000, "m": "Matching URL: equalTo /user"},
            {"t": 1000, "m": "URL Matched"},
            {"t": 1001, "m": "Matching Method: GET"},
            {"t": 1001, "m": "Method Matched"},
        ]
    )]
    result = format_sandbox_test_request(raw)
    assert result[0].matched is True
    assert result[0].mismatch_reasons == []


def test_formatter_invalid_base64_falls_back_to_raw():
    raw = [{"status": 200, "statusMessage": "OK", "headers": [], "body": "not-valid-base64!!!", "matchingLog": []}]
    result = format_sandbox_test_request(raw)
    assert result[0].body == "not-valid-base64!!!"
