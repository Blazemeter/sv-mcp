from conftest import load_fixture
from sv_mcp.formatters.asset import format_assets


def test_format_assets_happy_path():
    result = format_assets(load_fixture("asset"))
    assert len(result) == 1
    a = result[0]
    assert a.id == 777
    assert a.name == "keystore.jks"
    assert a.type == "CERTIFICATE"
    assert a.primaryMetadata == {"filename": "keystore.jks", "size": 4096}


def test_format_assets_null_primary_metadata():
    raw = [{"id": 1, "name": "file.txt", "type": "TEXT", "primaryMetadata": None}]
    result = format_assets(raw)
    assert result[0].primaryMetadata is None


def test_format_assets_empty_list():
    assert format_assets([]) == []
