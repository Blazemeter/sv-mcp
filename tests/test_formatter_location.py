from conftest import load_fixture
from sv_mcp.formatters.location import format_locations


def test_format_locations_happy_path():
    result = format_locations(load_fixture("location"))
    assert len(result) == 1
    loc = result[0]
    assert loc.harborId == "harbor-us-east"
    assert loc.shipId == "ship-001"
    assert loc.shipName == "US East (Private)"
    assert loc.kubernetes is False
    assert loc.portRange == "8000-9000"


def test_format_locations_empty_list():
    assert format_locations([]) == []


def test_format_locations_null_metadata_no_crash():
    raw = [{"harborId": "h1", "shipId": "s1", "shipName": "test", "kubernetes": False, "metadata": None}]
    result = format_locations(raw)
    assert result[0].portRange == ""


def test_format_locations_missing_metadata_key_no_crash():
    raw = [{"harborId": "h1", "shipId": "s1", "shipName": "test", "kubernetes": False}]
    result = format_locations(raw)
    assert result[0].portRange == ""


def test_format_locations_empty_metadata_no_crash():
    raw = [{"harborId": "h1", "shipId": "s1", "shipName": "test", "kubernetes": False, "metadata": {}}]
    result = format_locations(raw)
    assert result[0].portRange == ""
