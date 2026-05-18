from conftest import load_fixture
from sv_mcp.formatters.configuration import format_configurations


def test_format_configurations_happy_path():
    result = format_configurations(load_fixture("configuration"))
    assert len(result) == 1
    c = result[0]
    assert c.id == 101
    assert c.name == "AWS Config"
    assert c.description == "AWS S3 configuration"


def test_format_configurations_map_flattened():
    """configurationMap {key: {value: v, ...}} is flattened to {key: v}."""
    result = format_configurations(load_fixture("configuration"))
    assert result[0].configurationMap == {"bucket_name": "mybucket", "region": "us-east-1"}


def test_format_configurations_empty_map():
    raw = [{"id": 1, "name": "empty", "description": None, "configurationMap": {}}]
    result = format_configurations(raw)
    assert result[0].configurationMap == {}


def test_format_configurations_empty_list():
    assert format_configurations([]) == []


def test_format_configurations_missing_id_uses_none():
    raw = [{"name": "no-id", "configurationMap": {}}]
    result = format_configurations(raw)
    assert result[0].id is None
