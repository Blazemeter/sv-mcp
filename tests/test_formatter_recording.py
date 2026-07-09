from conftest import load_fixture
from sv_mcp.formatters.recording import format_recordings, format_recorded_messages


def test_format_recordings_happy_path():
    result = format_recordings(load_fixture("recording")["recordings"])
    assert len(result) == 1
    r = result[0]
    assert r.id == 1001
    assert r.name == "order-recording"
    assert r.serviceId == 341611


def test_format_recordings_runtime_config():
    result = format_recordings(load_fixture("recording")["recordings"])
    rc = result[0].runtimeConfig
    assert rc.replayCount == 2
    assert rc.delayBetweenReplays == 500
    assert rc.initialDelay == 0


def test_format_recordings_messages_inline():
    result = format_recordings(load_fixture("recording")["recordings"])
    msgs = result[0].messages
    assert len(msgs) == 1
    m = msgs[0]
    assert m.id == 2001
    assert m.messageType == "TEXT_MESSAGE"
    assert m.destination == "ORDER.IN"
    assert m.destinationType == "QUEUE"
    assert m.index == 0


def test_format_recordings_message_content_preserved():
    result = format_recordings(load_fixture("recording")["recordings"])
    m = result[0].messages[0]
    assert m.content == "eyJvcmRlcklkIjogIjEyMyJ9"


def test_format_recordings_tags():
    result = format_recordings(load_fixture("recording")["recordings"])
    assert result[0].tags == ["billing", "v2"]


def test_format_recordings_empty_list():
    assert format_recordings([]) == []


def test_format_recorded_messages_happy_path():
    result = format_recorded_messages(load_fixture("recording")["messages"])
    assert len(result) == 1
    m = result[0]
    assert m.id == 2001
    assert m.correlationId == "corr-001"
    assert len(m.headers) == 1
    assert m.headers[0].name == "JMS_MESSAGE_ID"
    assert len(m.properties) == 1
    assert m.properties[0].name == "orderType"
    assert m.properties[0].type == "STRING"


def test_format_recorded_messages_empty_list():
    assert format_recorded_messages([]) == []
