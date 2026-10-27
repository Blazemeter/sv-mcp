import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from conftest import load_fixture
from sv_mcp.formatters.test_data import format_tdm_assets
from sv_mcp.models.result import BaseResult
from sv_mcp.tools.vs.test_data_manager import build_data_model_content, build_data_model_content_from_csv
# Aliased so pytest does not try to collect the manager class as a test class
from sv_mcp.tools.vs.test_data_manager import TestDataManager as DataManager


def test_build_data_model_content_schema_and_kind():
    entities = [{"name": "model", "fields": [{"name": "id", "generator": "sequenceGenerator(1)"}]}]
    result = build_data_model_content("my-service", 123, entities)
    assert result["schema"] == "http://blazemeter.com/blazedata/schema"
    assert result["kind"] == "sdm"
    assert result["type"] == "object"


def test_build_data_model_content_title():
    entities = [{"name": "m", "fields": [{"name": "x", "generator": "randInt(1,10)"}]}]
    result = build_data_model_content("svc-name", 999, entities)
    assert result["title"] == "MS-svc-name-999"


def test_build_data_model_content_uuid_unique():
    entities = [{"name": "m", "fields": [{"name": "x", "generator": "randInt(1,10)"}]}]
    r1 = build_data_model_content("svc", 1, entities)
    r2 = build_data_model_content("svc", 1, entities)
    assert r1["id"] != r2["id"]


def test_build_data_model_content_entity_properties_and_requirements():
    entities = [{"name": "users", "fields": [
        {"name": "id", "generator": "sequenceGenerator(1)"},
        {"name": "email", "generator": "regExp('[a-z]{5}@[a-z]{3}\\.com')"},
    ], "repeat": 500}]
    result = build_data_model_content("svc", 42, entities)
    entity = result["entities"]["users"]
    assert entity["properties"] == {
        "id": {"type": "string"},
        "email": {"type": "string"},
    }
    assert entity["requirements"] == {
        "id": "sequenceGenerator(1)",
        "email": "regExp('[a-z]{5}@[a-z]{3}\\.com')",
    }
    assert entity["repeat"] == 500


def test_build_data_model_content_default_repeat():
    entities = [{"name": "m", "fields": [{"name": "x", "generator": "randInt(1,10)"}]}]
    result = build_data_model_content("svc", 1, entities)
    assert result["entities"]["m"]["repeat"] == 1000


def test_build_data_model_content_targets_and_datasources():
    entities = [{"name": "m", "fields": [{"name": "x", "generator": "randInt(1,10)"}]}]
    result = build_data_model_content("svc", 1, entities)
    entity = result["entities"]["m"]
    assert entity["targets"]["defaultCsv"] == {"type": "csv", "file": "model.csv", "isHeadless": False}
    assert entity["datasources"] == []


def test_build_data_model_content_multiple_entities():
    entities = [
        {"name": "users", "fields": [{"name": "id", "generator": "sequenceGenerator(1)"}]},
        {"name": "products", "fields": [{"name": "sku", "generator": "randText(5,10)"}]},
    ]
    result = build_data_model_content("svc", 1, entities)
    assert "users" in result["entities"]
    assert "products" in result["entities"]


def test_build_data_model_content_from_csv_schema_and_kind():
    result = build_data_model_content_from_csv("my-service", 123, "users.csv", ["id", "name"])
    assert result["schema"] == "http://blazemeter.com/blazedata/schema"
    assert result["kind"] == "sdm"
    assert result["type"] == "object"
    assert result["title"] == "MS-my-service-123"


def test_build_data_model_content_from_csv_entity_name_from_file_stem():
    result = build_data_model_content_from_csv("svc", 1, "addresses.csv", ["city"])
    assert "addresses_csv" in result["entities"]
    assert result["entities"]["addresses_csv"]["title"] == "addresses"


def test_build_data_model_content_from_csv_value_of_csv_generators():
    result = build_data_model_content_from_csv("svc", 7, "addresses.csv", ["city", "zip"])
    entity = result["entities"]["addresses_csv"]
    assert entity["properties"] == {
        "city": {"type": "string"},
        "zip": {"type": "string"},
    }
    assert entity["requirements"] == {
        "city": 'valueOfCSV("addresses.csv", "city")',
        "zip": 'valueOfCSV("addresses.csv", "zip")',
    }


def test_build_data_model_content_from_csv_targets_and_datasources():
    result = build_data_model_content_from_csv("svc", 1, "prices.csv", ["amount"])
    entity = result["entities"]["prices_csv"]
    assert entity["targets"] == {"prices_csv": {"type": "csv", "file": "prices.csv"}}
    assert entity["datasources"] == [
        {"id": {"fileName": "prices.csv"}, "type": "csv", "name": "prices.csv", "loop": False}
    ]


def test_build_data_model_content_from_csv_field_mappings_rename_column():
    result = build_data_model_content_from_csv(
        "svc", 1, "data.csv", ["c1"],
        field_mappings=[{"csv_column": "c1", "name": "renamed"}],
    )
    entity = result["entities"]["data_csv"]
    # field is renamed, but the generator still references the original CSV column
    assert entity["properties"] == {"renamed": {"type": "string"}}
    assert entity["requirements"] == {"renamed": 'valueOfCSV("data.csv", "c1")'}


def test_build_data_model_content_from_csv_uuid_unique():
    r1 = build_data_model_content_from_csv("svc", 1, "data.csv", ["a"])
    r2 = build_data_model_content_from_csv("svc", 1, "data.csv", ["a"])
    assert r1["id"] != r2["id"]


GLOBAL_ENTITY_ASSET = {
    "id": "ge-uuid-3333",
    "name": "global-entity-123",
    "displayName": "global-entity-123",
    "type": "global-entity",
    "packageId": "pkg-uuid-4444",
    "dataAccessible": True,
}

ENTITIES = [{"name": "orders", "fields": [{"name": "id", "generator": "sequenceGenerator(1)"}]}]


@pytest.fixture
def manager():
    return DataManager(token=MagicMock(), ctx=MagicMock())


@pytest.fixture
def csv_file(tmp_path):
    path = tmp_path / "orders.csv"
    path.write_text("id,status\n1,NEW\n")
    return str(path)


async def test_read_global_variables_returns_parsed_content(manager):
    asset = {**GLOBAL_ENTITY_ASSET, "data": {"content": '{"order_counter": "0"}'}}
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[asset])
        result = await manager.read_global_variables(workspace_id=1, service_id=123)
    assert mock_req.call_args.args[1] == "GET"
    assert mock_req.call_args.args[2] == "/workspaces/1/assets"
    assert mock_req.call_args.kwargs["params"] == [
        ("q", "type=global-entity"), ("q", "name=global-entity-123"), ("withData", "true"),
    ]
    assert result.error is None
    assert result.result == [{"order_counter": "0"}]


async def test_read_global_variables_empty_map(manager):
    asset = {**GLOBAL_ENTITY_ASSET, "data": {"content": {}}}
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[asset])
        result = await manager.read_global_variables(workspace_id=1, service_id=123)
    assert result.result == [{}]


async def test_read_global_variables_not_found(manager):
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        result = await manager.read_global_variables(workspace_id=1, service_id=123)
    assert "No global-entity asset found for service_id=123" in result.error
    assert "create_from_schema" in result.error
    assert result.result is None


async def test_read_global_variables_passes_fetch_error_through(manager):
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        mock_req.return_value = BaseResult(error="Access forbidden")
        result = await manager.read_global_variables(workspace_id=1, service_id=123)
    assert result.error == "Access forbidden"


async def test_set_global_variables_replaces_content_and_keeps_asset_fields(manager):
    raw_asset = {**GLOBAL_ENTITY_ASSET, "data": {"content": {"stale": "1"}}}
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        mock_req.side_effect = [BaseResult(result=[raw_asset]), BaseResult(result=[])]
        await manager.set_global_variables(
            workspace_id=1, service_id=123, global_variables={"order_counter": "5"}
        )
    fetch_call, put_call = mock_req.call_args_list
    assert fetch_call.args[1] == "GET"
    assert fetch_call.kwargs["params"] == [
        ("q", "type=global-entity"), ("q", "name=global-entity-123"), ("withData", "false"),
    ]
    assert put_call.args[1] == "PUT"
    assert put_call.args[2] == "/workspaces/1/assets/ge-uuid-3333"
    assert put_call.kwargs["result_formatter"] is format_tdm_assets
    assert put_call.kwargs["json"] == {
        **GLOBAL_ENTITY_ASSET,
        "data": {
            "fileName": "global-entity.json",
            "contentType": "application/json",
            "content": {"order_counter": "5"},
        },
    }


async def test_set_global_variables_not_found_makes_no_put(manager):
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        result = await manager.set_global_variables(
            workspace_id=1, service_id=123, global_variables={"order_counter": "0"}
        )
    assert mock_req.call_count == 1
    assert "No global-entity asset found for service_id=123" in result.error


async def test_update_sets_global_variables_when_given(manager):
    manager.set_global_variables = AsyncMock(return_value=BaseResult(result=[]))
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        mock_req.side_effect = [BaseResult(result=load_fixture("tdm_asset")), BaseResult(result=[])]
        result = await manager.update(
            1, 123, "my-service", ENTITIES, global_variables={"order_counter": "0"}
        )
    assert mock_req.call_args.args[1] == "PUT"
    manager.set_global_variables.assert_awaited_once_with(1, 123, {"order_counter": "0"})
    assert result.error is None


async def test_update_skips_global_variables_when_none(manager):
    manager.set_global_variables = AsyncMock(return_value=BaseResult(result=[]))
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        mock_req.side_effect = [BaseResult(result=load_fixture("tdm_asset")), BaseResult(result=[])]
        await manager.update(1, 123, "my-service", ENTITIES)
    manager.set_global_variables.assert_not_awaited()


async def test_update_warns_when_global_variables_fail(manager):
    manager.set_global_variables = AsyncMock(return_value=BaseResult(error="No global-entity asset found"))
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        mock_req.side_effect = [BaseResult(result=load_fixture("tdm_asset")), BaseResult(result=[])]
        result = await manager.update(
            1, 123, "my-service", ENTITIES, global_variables={"order_counter": "0"}
        )
    assert result.error is None
    assert result.warning == ["Data model updated, but global variables were not: No global-entity asset found"]


async def test_update_rejects_non_string_global_variables_before_any_call(manager):
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        result = await manager.update(1, 123, "my-service", ENTITIES, global_variables={"order_counter": 0})
    assert result.error.startswith("global_variables must be a flat map of names to string values")
    mock_req.assert_not_called()


async def test_set_global_variables_rejects_non_dict(manager):
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        result = await manager.set_global_variables(1, 123, '{"order_counter": "0"}')
    assert result.error.startswith("global_variables must be a flat map")
    mock_req.assert_not_called()


async def test_update_skips_global_variables_when_data_model_put_fails(manager):
    manager.set_global_variables = AsyncMock(return_value=BaseResult(result=[]))
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        mock_req.side_effect = [BaseResult(result=load_fixture("tdm_asset")), BaseResult(error="PUT failed")]
        result = await manager.update(
            1, 123, "my-service", ENTITIES, global_variables={"order_counter": "0"}
        )
    assert result.error == "PUT failed"
    manager.set_global_variables.assert_not_awaited()


async def test_update_from_csv_sets_global_variables_when_given(manager, csv_file):
    manager.set_global_variables = AsyncMock(return_value=BaseResult(result=[]))
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        mock_req.side_effect = [BaseResult(result=load_fixture("tdm_asset")), BaseResult(result=[])]
        result = await manager.update_from_csv(
            1, 123, "my-service", csv_file, global_variables={"order_counter": "0"}
        )
    assert mock_req.call_args.args[1] == "PUT"
    manager.set_global_variables.assert_awaited_once_with(1, 123, {"order_counter": "0"})
    assert result.error is None


async def test_update_from_csv_skips_global_variables_when_none(manager, csv_file):
    manager.set_global_variables = AsyncMock(return_value=BaseResult(result=[]))
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        mock_req.side_effect = [BaseResult(result=load_fixture("tdm_asset")), BaseResult(result=[])]
        await manager.update_from_csv(1, 123, "my-service", csv_file)
    manager.set_global_variables.assert_not_awaited()


async def test_update_from_csv_warns_when_global_variables_fail(manager, csv_file):
    manager.set_global_variables = AsyncMock(return_value=BaseResult(error="No global-entity asset found"))
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        mock_req.side_effect = [BaseResult(result=load_fixture("tdm_asset")), BaseResult(result=[])]
        result = await manager.update_from_csv(
            1, 123, "my-service", csv_file, global_variables={"order_counter": "0"}
        )
    assert result.error is None
    assert result.warning == ["Data model updated, but global variables were not: No global-entity asset found"]


async def test_update_from_csv_with_upload_sets_global_variables_after_upload(manager, csv_file):
    manager.set_global_variables = AsyncMock(return_value=BaseResult(result=[]))
    manager._upload_csv_file = AsyncMock(return_value=BaseResult(result=[]))
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        mock_req.side_effect = [BaseResult(result=load_fixture("tdm_asset")), BaseResult(result=[])]
        result = await manager.update_from_csv(
            1, 123, "my-service", csv_file, upload_csv=True, global_variables={"order_counter": "0"}
        )
    manager._upload_csv_file.assert_awaited_once()
    manager.set_global_variables.assert_awaited_once_with(1, 123, {"order_counter": "0"})
    assert result.error is None


async def test_global_variables_ignore_assets_whose_name_only_partially_matches(manager):
    """set_global_variables replaces the whole map, so it must never write another service's asset."""
    other_service_asset = {**GLOBAL_ENTITY_ASSET, "id": "ge-other", "name": "global-entity-1234"}
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[other_service_asset])
        result = await manager.set_global_variables(
            workspace_id=1, service_id=123, global_variables={"order_counter": "0"}
        )
    assert mock_req.call_count == 1
    assert "No global-entity asset found for service_id=123" in result.error


async def test_create_from_schema_rejects_non_string_global_variables_before_any_call(manager):
    with patch("sv_mcp.tools.vs.test_data_manager.tdm_api_request") as mock_req:
        result = await manager.create_from_schema(1, 123, "my-service", ENTITIES, global_variables={"count": 0})
    mock_req.assert_not_called()
    assert result.error.startswith("global_variables must be a flat map")
