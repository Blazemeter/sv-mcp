from conftest import load_fixture
from sv_mcp.formatters.execution import (
    format_executions,
    format_executions_detailed,
    format_executions_status,
)


def test_format_executions_happy_path():
    result = format_executions(load_fixture("execution"))
    assert len(result) == 1
    e = result[0]
    assert e.execution_id == 999
    assert e.execution_name == "Load Test Run"
    assert e.project_id == 1001
    assert "999" in e.execution_url


def test_format_executions_empty_list():
    assert format_executions([]) == []


def test_format_executions_detailed_happy_path():
    result = format_executions_detailed(load_fixture("execution"))
    e = result[0]
    assert e.execution_id == 999
    assert e.execution_status == "pass"
    assert e.created is not None
    assert e.ended is not None


def test_format_executions_detailed_null_timestamps_no_crash():
    raw = [{"id": 1, "name": "test", "projectId": 1, "created": None, "updated": None, "ended": None, "reportStatus": "unset"}]
    result = format_executions_detailed(raw)
    assert result[0].created is None
    assert result[0].ended is None


def test_format_executions_status_happy_path():
    raw = [{
        "executionStep": "running",
        "statuses": {"pending": 0, "booting": 10, "downloading": 0, "ready": 80, "ended": 10}
    }]
    result = format_executions_status(raw)
    assert result[0].execution_step == "running"
    assert result[0].progress_percent == 10
    assert result[0].execution_statuses.ready_percent == 80


def test_format_executions_status_missing_statuses_key_no_crash():
    """Bug fix: absent 'statuses' key must not crash with AttributeError."""
    raw = [{"executionStep": "pending"}]
    result = format_executions_status(raw)
    assert result[0].execution_step == "pending"
    assert result[0].progress_percent == 0
