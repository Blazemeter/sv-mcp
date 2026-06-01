from conftest import load_fixture
from sv_mcp.formatters.test_data import format_tdm_packages, format_tdm_assets


def test_format_tdm_packages_happy_path():
    result = format_tdm_packages(load_fixture("tdm_package"))
    assert len(result) == 1
    p = result[0]
    assert p.id == "pkg-uuid-1111"
    assert p.name == "MS-my-service-123"
    assert p.version == "1.0.0"


def test_format_tdm_packages_empty():
    assert format_tdm_packages([]) == []


def test_format_tdm_packages_missing_fields():
    result = format_tdm_packages([{"id": "abc"}])
    assert result[0].id == "abc"
    assert result[0].name is None
    assert result[0].version is None


def test_format_tdm_assets_happy_path():
    result = format_tdm_assets(load_fixture("tdm_asset"))
    assert len(result) == 1
    a = result[0]
    assert a.id == "asset-uuid-2222"
    assert a.name == "MS-my-service-123"
    assert a.type == "data-model"
    assert a.packageId == "pkg-uuid-1111"


def test_format_tdm_assets_empty():
    assert format_tdm_assets([]) == []


def test_format_tdm_assets_missing_fields():
    result = format_tdm_assets([{"id": "xyz", "type": "mock-svc"}])
    assert result[0].id == "xyz"
    assert result[0].type == "mock-svc"
    assert result[0].name is None
    assert result[0].packageId is None
