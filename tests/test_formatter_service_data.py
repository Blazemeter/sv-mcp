from conftest import load_fixture
from sv_mcp.formatters.service_data import format_service_data


def test_format_service_data_happy_path():
    result = format_service_data(load_fixture("service_data"))
    assert len(result) == 1
    data = result[0]
    assert data.links.dataFileLink == "https://storage.blazemeter.com/blazedata/55001/data.json"
    assert data.links.previewFileLink == "https://storage.blazemeter.com/blazedata/55001/preview.json"
    assert data.links.modelFileLink == "https://storage.blazemeter.com/blazedata/55001/model.json"
    assert data.globalVariables == {"order_counter": "3", "region": "eu-west"}
    assert data.dataSettings is None


def test_format_service_data_missing_links_and_null_variables():
    raw = [{"blazeDataDetailLinksDto": None, "globalVariables": None}]
    result = format_service_data(raw)
    assert result[0].links is None
    assert result[0].globalVariables == {}


def test_format_service_data_settings_passed_through():
    settings = {"anyKey": ["any", "shape"], "nested": {"value": 1}}
    result = format_service_data([{"dataSettings": settings}])
    assert result[0].dataSettings == settings


def test_format_service_data_empty_list():
    assert format_service_data([]) == []


def test_format_service_data_keeps_numeric_variables():
    # INCREMENT_VALUE can leave a number in the map
    result = format_service_data([{"globalVariables": {"order_counter": 4}}])
    assert result[0].globalVariables == {"order_counter": 4}
