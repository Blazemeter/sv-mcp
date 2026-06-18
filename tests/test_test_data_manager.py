from sv_mcp.tools.vs.test_data_manager import build_data_model_content, build_data_model_content_from_csv


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
