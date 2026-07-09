import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sv_mcp.models.result import BaseResult
from sv_mcp.models.vs.sandbox_response import SandboxResponse
from sv_mcp.tools.vs.http_transaction_manager import HttpTransactionManager

pytestmark = pytest.mark.asyncio


@pytest.fixture
def manager():
    return HttpTransactionManager(token=MagicMock(), ctx=MagicMock())


def _make_transaction(id=42):
    t = MagicMock()
    t.id = id
    return t


def _matched_response():
    return SandboxResponse(status=200, statusMessage="OK", matchingLog=[])


def _unmatched_response(reason="Method mismatch"):
    from sv_mcp.models.vs.matching_log_entry import MatchingLogEntry
    return SandboxResponse(
        status=404, statusMessage="Not Found",
        matchingLog=[MatchingLogEntry(t=1000, m=reason)]
    )


async def test_create_and_test_all_pass(manager):
    manager.create = AsyncMock(return_value=BaseResult(result=[_make_transaction()]))
    mock_sb = MagicMock()
    mock_sb.init = AsyncMock(return_value=BaseResult(result=[MagicMock()]))
    mock_sb.test_request = AsyncMock(return_value=BaseResult(result=[_matched_response()]))

    with patch("sv_mcp.tools.vs.http_transaction_manager.SandboxManager", return_value=mock_sb):
        result = await manager.create_and_test(
            transaction_name="t", workspace_id=1, service_id=2,
            dsl={}, delay=None,
            test_cases=[{"method": "GET", "path": "/ping", "name": "svc"}],
        )

    assert result.error is None
    assert result.warning is None
    assert result.result[0].matched is True
    assert any("tests_passed=1" in s for s in result.info)
    assert any("tests_total=1" in s for s in result.info)


async def test_create_and_test_all_fail(manager):
    manager.create = AsyncMock(return_value=BaseResult(result=[_make_transaction()]))
    mock_sb = MagicMock()
    mock_sb.init = AsyncMock(return_value=BaseResult(result=[MagicMock()]))
    mock_sb.test_request = AsyncMock(return_value=BaseResult(result=[_unmatched_response()]))

    with patch("sv_mcp.tools.vs.http_transaction_manager.SandboxManager", return_value=mock_sb):
        result = await manager.create_and_test(
            transaction_name="t", workspace_id=1, service_id=2,
            dsl={}, delay=None,
            test_cases=[{"method": "POST", "path": "/ping", "name": "svc"}],
        )

    assert result.error is not None
    assert "All 1 test case(s) failed" in result.error
    assert result.result[0].matched is False


async def test_create_and_test_partial_fail(manager):
    manager.create = AsyncMock(return_value=BaseResult(result=[_make_transaction()]))
    mock_sb = MagicMock()
    mock_sb.init = AsyncMock(return_value=BaseResult(result=[MagicMock()]))
    mock_sb.test_request = AsyncMock(side_effect=[
        BaseResult(result=[_matched_response()]),
        BaseResult(result=[_unmatched_response()]),
    ])

    with patch("sv_mcp.tools.vs.http_transaction_manager.SandboxManager", return_value=mock_sb):
        result = await manager.create_and_test(
            transaction_name="t", workspace_id=1, service_id=2,
            dsl={}, delay=None,
            test_cases=[
                {"method": "GET", "path": "/ping", "name": "svc"},
                {"method": "POST", "path": "/ping", "name": "svc"},
            ],
        )

    assert result.error is None
    assert result.warning is not None
    assert "1 of 2" in result.warning[0]


async def test_create_and_test_create_failure_propagated(manager):
    manager.create = AsyncMock(return_value=BaseResult(error="API error"))

    with patch("sv_mcp.tools.vs.http_transaction_manager.SandboxManager"):
        result = await manager.create_and_test(
            transaction_name="t", workspace_id=1, service_id=2,
            dsl={}, delay=None,
            test_cases=[{"method": "GET", "path": "/ping", "name": "svc"}],
        )

    assert result.error == "API error"


async def test_create_and_test_sandbox_init_failure_includes_transaction_id(manager):
    manager.create = AsyncMock(return_value=BaseResult(result=[_make_transaction(id=99)]))
    mock_sb = MagicMock()
    mock_sb.init = AsyncMock(return_value=BaseResult(error="Sandbox unreachable"))

    with patch("sv_mcp.tools.vs.http_transaction_manager.SandboxManager", return_value=mock_sb):
        result = await manager.create_and_test(
            transaction_name="t", workspace_id=1, service_id=2,
            dsl={}, delay=None,
            test_cases=[{"method": "GET", "path": "/ping", "name": "svc"}],
        )

    assert result.error == "Sandbox unreachable"
    assert any("transaction_id=99" in s for s in result.info)


async def test_create_and_test_empty_result_counted_as_failure(manager):
    manager.create = AsyncMock(return_value=BaseResult(result=[_make_transaction()]))
    mock_sb = MagicMock()
    mock_sb.init = AsyncMock(return_value=BaseResult(result=[MagicMock()]))
    mock_sb.test_request = AsyncMock(return_value=BaseResult(result=[]))

    with patch("sv_mcp.tools.vs.http_transaction_manager.SandboxManager", return_value=mock_sb):
        result = await manager.create_and_test(
            transaction_name="t", workspace_id=1, service_id=2,
            dsl={}, delay=None,
            test_cases=[{"method": "GET", "path": "/ping", "name": "svc"}],
        )

    assert result.error is not None
    assert "All 1 test case(s) failed" in result.error
    assert len(result.result) == 1
    assert result.result[0].matched is False


async def test_create_and_test_test_request_error_counted_as_failure(manager):
    manager.create = AsyncMock(return_value=BaseResult(result=[_make_transaction()]))
    mock_sb = MagicMock()
    mock_sb.init = AsyncMock(return_value=BaseResult(result=[MagicMock()]))
    mock_sb.test_request = AsyncMock(return_value=BaseResult(error="Connection refused"))

    with patch("sv_mcp.tools.vs.http_transaction_manager.SandboxManager", return_value=mock_sb):
        result = await manager.create_and_test(
            transaction_name="t", workspace_id=1, service_id=2,
            dsl={}, delay=None,
            test_cases=[{"method": "GET", "path": "/ping", "name": "svc"}],
        )

    assert result.error is not None
    assert "All 1 test case(s) failed" in result.error
    assert result.result[0].matched is False
    assert "Connection refused" in result.result[0].mismatch_reasons[0]
