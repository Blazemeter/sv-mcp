import base64

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sv_mcp.models.result import BaseResult
from sv_mcp.models.vs.http_transaction import HttpTransaction
from sv_mcp.models.vs.matcher_dsl import MatcherDsl
from sv_mcp.tools.vs.http_transaction_manager import HttpTransactionManager


@pytest.fixture
def manager():
    return HttpTransactionManager(token=MagicMock(), ctx=MagicMock())


def _dsl_with_body_matcher(matching_value=None, sample_body=None):
    return {
        "requestDsl": {
            "method": "POST",
            "url": {"key": "url", "matcherName": "equals_url", "matchingValue": "/test"},
            "body": [
                {
                    "key": "body",
                    "matcherName": "equals_json",
                    "matchingValue": matching_value,
                    "sampleBody": sample_body,
                }
            ],
        },
        "responseDsl": {"status": 200},
    }


async def test_create_encodes_body_matcher_matching_value(manager):
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create(
            transaction_name="t1",
            workspace_id=1,
            service_id=2,
            dsl=_dsl_with_body_matcher(matching_value='{"foo": "bar"}'),
            delay=None,
        )
    body = mock_req.call_args.kwargs["json"]
    matcher = body["transactions"][0]["dsl"]["requestDsl"]["body"][0]
    assert base64.b64decode(matcher["matchingValue"]).decode() == '{"foo": "bar"}'


async def test_create_encodes_body_matcher_sample_body(manager):
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create(
            transaction_name="t1",
            workspace_id=1,
            service_id=2,
            dsl=_dsl_with_body_matcher(matching_value='{"foo": "bar"}', sample_body='{"foo": "bar"}'),
            delay=None,
        )
    body = mock_req.call_args.kwargs["json"]
    matcher = body["transactions"][0]["dsl"]["requestDsl"]["body"][0]
    assert base64.b64decode(matcher["sampleBody"]).decode() == '{"foo": "bar"}'


async def test_create_leaves_missing_sample_body_untouched(manager):
    """sampleBody is optional — no crash, no fabricated value, when caller doesn't set it."""
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create(
            transaction_name="t1",
            workspace_id=1,
            service_id=2,
            dsl=_dsl_with_body_matcher(matching_value='{"foo": "bar"}'),
            delay=None,
        )
    body = mock_req.call_args.kwargs["json"]
    matcher = body["transactions"][0]["dsl"]["requestDsl"]["body"][0]
    assert matcher["sampleBody"] is None


async def test_create_applies_top_level_sample_body_fallback_to_body_matcher(manager):
    """Models consistently send sampleBody as a top-level arg sibling to dsl/name instead of
    nesting it in the body matcher (3/3 in the real chat log). Without a fallback this is
    silently discarded — the dispatcher/manager never reads a top-level sampleBody at all."""
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create(
            transaction_name="t1",
            workspace_id=1,
            service_id=2,
            dsl=_dsl_with_body_matcher(matching_value='{"foo": "bar"}'),
            delay=None,
            sample_body='{"foo": "bar"}',
        )
    body = mock_req.call_args.kwargs["json"]
    matcher = body["transactions"][0]["dsl"]["requestDsl"]["body"][0]
    assert base64.b64decode(matcher["sampleBody"]).decode() == '{"foo": "bar"}'


async def test_create_top_level_sample_body_does_not_override_explicit_matcher_sample_body(manager):
    """The per-matcher sampleBody stays the primary/explicit path — the top-level fallback
    must not clobber a value the caller already set correctly on the matcher itself."""
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create(
            transaction_name="t1",
            workspace_id=1,
            service_id=2,
            dsl=_dsl_with_body_matcher(matching_value='{"foo": "bar"}', sample_body="explicit"),
            delay=None,
            sample_body="fallback",
        )
    body = mock_req.call_args.kwargs["json"]
    matcher = body["transactions"][0]["dsl"]["requestDsl"]["body"][0]
    assert base64.b64decode(matcher["sampleBody"]).decode() == "explicit"


async def test_create_without_top_level_sample_body_is_noop(manager):
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create(
            transaction_name="t1",
            workspace_id=1,
            service_id=2,
            dsl=_dsl_with_body_matcher(matching_value='{"foo": "bar"}'),
            delay=None,
        )
    body = mock_req.call_args.kwargs["json"]
    matcher = body["transactions"][0]["dsl"]["requestDsl"]["body"][0]
    assert matcher["sampleBody"] is None


async def test_update_applies_top_level_sample_body_fallback_to_body_matcher(manager):
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.update(
            id=10,
            transaction_name="t1",
            workspace_id=1,
            dsl=_dsl_with_body_matcher(matching_value='{"foo": "bar"}'),
            delay=None,
            sample_body='{"foo": "bar"}',
        )
    body = mock_req.call_args.kwargs["json"]
    matcher = body["dsl"]["requestDsl"]["body"][0]
    assert base64.b64decode(matcher["sampleBody"]).decode() == '{"foo": "bar"}'


async def test_update_encodes_body_matcher_matching_value(manager):
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.update(
            id=10,
            transaction_name="t1",
            workspace_id=1,
            dsl=_dsl_with_body_matcher(matching_value='{"foo": "bar"}'),
            delay=None,
        )
    body = mock_req.call_args.kwargs["json"]
    matcher = body["dsl"]["requestDsl"]["body"][0]
    assert base64.b64decode(matcher["matchingValue"]).decode() == '{"foo": "bar"}'


async def test_update_encodes_body_matcher_sample_body(manager):
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.update(
            id=10,
            transaction_name="t1",
            workspace_id=1,
            dsl=_dsl_with_body_matcher(matching_value='{"foo": "bar"}', sample_body='{"foo": "bar"}'),
            delay=None,
        )
    body = mock_req.call_args.kwargs["json"]
    matcher = body["dsl"]["requestDsl"]["body"][0]
    assert base64.b64decode(matcher["sampleBody"]).decode() == '{"foo": "bar"}'


async def test_update_top_level_sample_body_does_not_override_explicit_matcher_sample_body(manager):
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.update(
            id=10,
            transaction_name="t1",
            workspace_id=1,
            dsl=_dsl_with_body_matcher(matching_value='{"foo": "bar"}', sample_body="explicit"),
            delay=None,
            sample_body="fallback",
        )
    body = mock_req.call_args.kwargs["json"]
    matcher = body["dsl"]["requestDsl"]["body"][0]
    assert base64.b64decode(matcher["sampleBody"]).decode() == "explicit"


async def test_create_warns_when_sample_body_has_no_body_matcher_to_attach_to(manager):
    """Same 'silently discarded, no signal' failure mode the fix targets, just narrower:
    a top-level sampleBody with an empty (or absent) body matcher list must not vanish
    without at least a warning."""
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        result = await manager.create(
            transaction_name="t1",
            workspace_id=1,
            service_id=2,
            dsl={"requestDsl": {"body": []}, "responseDsl": {"status": 200}},
            delay=None,
            sample_body="orphaned sample body",
        )
    assert result.warning
    assert any("no body matcher" in w for w in result.warning)


async def test_create_no_warning_when_body_matcher_receives_sample_body(manager):
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        result = await manager.create(
            transaction_name="t1",
            workspace_id=1,
            service_id=2,
            dsl=_dsl_with_body_matcher(matching_value='{"foo": "bar"}'),
            delay=None,
            sample_body='{"foo": "bar"}',
        )
    assert result.warning is None


async def test_update_warns_when_sample_body_has_no_body_matcher_to_attach_to(manager):
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        result = await manager.update(
            id=10,
            transaction_name="t1",
            workspace_id=1,
            dsl={"requestDsl": {"body": []}, "responseDsl": {"status": 200}},
            delay=None,
            sample_body="orphaned sample body",
        )
    assert result.warning
    assert any("no body matcher" in w for w in result.warning)


async def test_create_and_test_forwards_sample_body_to_create():
    """create_and_test is the tool's own documented-preferred path whenever the DSL has
    Handlebars templates — exactly the scenario likely to carry a sample body. It must not
    silently drop sample_body by failing to forward it to create()."""
    manager = HttpTransactionManager(token=MagicMock(), ctx=MagicMock())
    manager.create = AsyncMock(return_value=BaseResult(result=[MagicMock(id=1)]))
    mock_sb = MagicMock()
    mock_sb.init = AsyncMock(return_value=BaseResult(result=[MagicMock()]))
    mock_sb.test_request = AsyncMock(return_value=BaseResult(result=[MagicMock(matched=True)]))

    with patch("sv_mcp.tools.vs.http_transaction_manager.SandboxManager", return_value=mock_sb):
        await manager.create_and_test(
            transaction_name="t1", workspace_id=1, service_id=2,
            dsl={}, delay=None,
            test_cases=[{"method": "GET", "path": "/ping", "name": "svc"}],
            sample_body="hello",
        )

    manager.create.assert_awaited_once_with("t1", 1, 2, {}, None, "hello")


async def test_create_and_test_propagates_create_warning():
    manager = HttpTransactionManager(token=MagicMock(), ctx=MagicMock())
    manager.create = AsyncMock(return_value=BaseResult(
        result=[MagicMock(id=1)], warning=["sampleBody was provided but the transaction has no body matcher"]
    ))
    mock_sb = MagicMock()
    mock_sb.init = AsyncMock(return_value=BaseResult(result=[MagicMock()]))
    mock_sb.test_request = AsyncMock(return_value=BaseResult(result=[MagicMock(matched=True)]))

    with patch("sv_mcp.tools.vs.http_transaction_manager.SandboxManager", return_value=mock_sb):
        result = await manager.create_and_test(
            transaction_name="t1", workspace_id=1, service_id=2,
            dsl={}, delay=None,
            test_cases=[{"method": "GET", "path": "/ping", "name": "svc"}],
            sample_body="orphaned",
        )

    assert any("no body matcher" in w for w in result.warning)


async def test_create_leaves_non_body_matcher_sample_body_untouched(manager):
    """The encode loop only iterates request.body — a sampleBody set on the url matcher
    (or any non-body matcher) must be sent through as-is, not base64-encoded."""
    dsl = _dsl_with_body_matcher(matching_value='{"foo": "bar"}')
    dsl["requestDsl"]["url"]["sampleBody"] = "not-base64-should-be-untouched"
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create(
            transaction_name="t1", workspace_id=1, service_id=2, dsl=dsl, delay=None,
        )
    body = mock_req.call_args.kwargs["json"]
    url_matcher = body["transactions"][0]["dsl"]["requestDsl"]["url"]
    assert url_matcher["sampleBody"] == "not-base64-should-be-untouched"


def test_matcher_dsl_sample_body_field_round_trips():
    matcher = MatcherDsl(matcherName="equals_json", matchingValue="x", sampleBody="hello")
    assert matcher.model_dump()["sampleBody"] == "hello"


def test_matcher_dsl_sample_body_defaults_to_none():
    matcher = MatcherDsl(matcherName="equals_json", matchingValue="x")
    assert matcher.sampleBody is None


def test_http_transaction_preserves_unexpected_extra_field():
    """Sibling DSL models (GenericDsl/RequestDsl/MatcherDsl) all use extra='allow';
    HttpTransaction must match, or a model-supplied top-level field silently vanishes."""
    txn = HttpTransaction(
        id=1,
        name="t1",
        dsl={"requestDsl": {}, "responseDsl": {"status": 200}},
        sampleBody="hello",
    )
    assert txn.model_dump()["sampleBody"] == "hello"


class _CapturingMCP:
    def __init__(self):
        self.descriptions = {}

    def tool(self, name, description):
        self.descriptions[name] = description
        return lambda fn: fn


def test_create_and_test_description_documents_body_not_content():
    """create_and_test test_cases go through SandboxManager.test_request, whose backend
    field is `body` (plain text, encoded by the tool). Advertising `content (str base64)`
    here made models send a body the backend silently drops."""
    from sv_mcp.tools.vs import http_transaction_manager

    mcp = _CapturingMCP()
    http_transaction_manager.register(mcp, token=None)
    description = mcp.descriptions["virtual_services_http_transaction"]
    test_cases_doc = description.split("test_cases (list[SandboxRequest])", 1)[1].split("sampleBody", 1)[0]
    assert "content" not in test_cases_doc
    assert "body" in test_cases_doc


def _dsl_with_response_content(content):
    response = {"status": 201}
    if content is not None:
        response["content"] = content
    return {
        "requestDsl": {"method": "POST", "url": {"key": "url", "matcherName": "equals_url", "matchingValue": "/x"}},
        "responseDsl": response,
    }


@pytest.mark.asyncio
async def test_create_encodes_plain_text_response_content(manager):
    """The backend rejects non-base64 responseDsl.content ("Request body is empty or has
    invalid format."), so plain text described by a user must be encoded by the tool."""
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create("t", 1, 2, _dsl_with_response_content('{"accepted": true}'), None)
    content = mock_req.call_args.kwargs["json"]["transactions"][0]["dsl"]["responseDsl"]["content"]
    assert base64.b64decode(content).decode() == '{"accepted": true}'


@pytest.mark.asyncio
async def test_create_preserves_base64_response_content(manager):
    """convert_template returns base64 and the docs tell models to use it as-is -
    it must not be double-encoded."""
    encoded = base64.b64encode(b'{"accepted": true}').decode()
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create("t", 1, 2, _dsl_with_response_content(encoded), None)
    content = mock_req.call_args.kwargs["json"]["transactions"][0]["dsl"]["responseDsl"]["content"]
    assert content == encoded


@pytest.mark.asyncio
async def test_update_encodes_plain_text_response_content(manager):
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.update(10, "t", 1, _dsl_with_response_content('{"accepted": true}'), None)
    content = mock_req.call_args.kwargs["json"]["dsl"]["responseDsl"]["content"]
    assert base64.b64decode(content).decode() == '{"accepted": true}'


@pytest.mark.asyncio
async def test_create_without_response_content_leaves_it_absent(manager):
    with patch("sv_mcp.tools.vs.http_transaction_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create("t", 1, 2, _dsl_with_response_content(None), None)
    response = mock_req.call_args.kwargs["json"]["transactions"][0]["dsl"]["responseDsl"]
    assert "content" not in response


def _http_tool_description():
    from sv_mcp.tools.vs import http_transaction_manager
    mcp = _CapturingMCP()
    http_transaction_manager.register(mcp, token=None)
    return mcp.descriptions["virtual_services_http_transaction"]


def test_description_says_dataset_variables_are_not_wildcards():
    """A model used ${shipmentId} in an equals_json matcher to mean "any id" and got a 404:
    without a dataset it is matched as literal text."""
    description = _http_tool_description()
    assert "not a wildcard" in description
    assert "matching(.+)" in description


def test_description_says_to_quote_template_strings_in_json():
    """A model wrote {"shipmentId": {{jsonPath ...}}} and the mock returned invalid JSON
    ({"shipmentId": S-400}) - helper output is raw text, so strings need quotes."""
    description = _http_tool_description()
    assert "\"{{jsonPath request.body '$.id'}}\"" in description
