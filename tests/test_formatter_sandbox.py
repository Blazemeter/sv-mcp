from sv_mcp.formatters.sandbox import format_sandbox


def test_format_sandbox_happy_path():
    raw = [{"serviceId": 341611, "userId": 12345, "transactionId": 6485927}]
    result = format_sandbox(raw)
    assert len(result) == 1
    s = result[0]
    assert s.serviceId == 341611
    assert s.userId == 12345
    assert s.transactionId == 6485927


def test_format_sandbox_empty_list():
    assert format_sandbox([]) == []


def test_format_sandbox_missing_optional_fields_no_crash():
    raw = [{}]
    result = format_sandbox(raw)
    assert result[0].serviceId is None
    assert result[0].userId is None
    assert result[0].transactionId is None
