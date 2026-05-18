from conftest import load_fixture
from sv_mcp.formatters.tracking import format_trackings, format_asset_trackings


def test_format_trackings_happy_path():
    fixture = load_fixture("tracking")
    result = format_trackings(fixture["master"])
    assert len(result) == 1
    t = result[0]
    assert t.trackingId == "uuid-master-001"
    assert t.status == "FINISHED"
    assert t.errors == []
    assert t.data is not None
    assert t.data.dataType == "MASTER_TRACKING"


def test_format_trackings_empty_list():
    assert format_trackings([]) == []


def test_format_trackings_null_data_uses_defaults():
    """Bug fix: None data must not crash with TypeError."""
    raw = [{"trackingId": "uuid-x", "status": "PENDING", "errors": [], "warnings": [], "data": None}]
    result = format_trackings(raw)
    assert result[0].trackingId == "uuid-x"
    assert result[0].data is not None
    assert result[0].data.dataType == "MASTER_TRACKING"


def test_format_asset_trackings_happy_path():
    fixture = load_fixture("tracking")
    result = format_asset_trackings(fixture["asset"])
    assert len(result) == 1
    t = result[0]
    assert t.trackingId == "uuid-asset-002"
    assert t.data is not None
    assert t.data.dataType == "FILE_UPLOAD"
    assert t.data.assetId == 777


def test_format_asset_trackings_null_data_uses_defaults():
    """Bug fix: None data must not crash with TypeError."""
    raw = [{"trackingId": "uuid-y", "status": "PENDING", "errors": [], "warnings": [], "data": None}]
    result = format_asset_trackings(raw)
    assert result[0].trackingId == "uuid-y"
    assert result[0].data is not None
    assert result[0].data.dataType == "FILE_UPLOAD"
