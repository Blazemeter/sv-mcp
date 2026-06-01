from sv_mcp.tools.vs.test_data_manager import build_data_model_content, build_entities_from_csv_headers


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


def test_build_entities_from_csv_headers_generators():
    entities = build_entities_from_csv_headers(["id", "name", "email"], "users.csv", "model", 500)
    assert len(entities) == 1
    entity = entities[0]
    assert entity["name"] == "model"
    assert entity["repeat"] == 500
    assert entity["fields"] == [
        {"name": "id", "generator": 'randFromCSV("users.csv", "id")'},
        {"name": "name", "generator": 'randFromCSV("users.csv", "name")'},
        {"name": "email", "generator": 'randFromCSV("users.csv", "email")'},
    ]


def test_build_entities_from_csv_headers_default_repeat():
    entities = build_entities_from_csv_headers(["a", "b"], "data.csv", "model")
    assert entities[0]["repeat"] == 1000


def test_build_entities_from_csv_headers_custom_entity_name():
    entities = build_entities_from_csv_headers(["x"], "test.csv", "my_entity", 200)
    assert entities[0]["name"] == "my_entity"
    assert entities[0]["repeat"] == 200


def test_build_entities_from_csv_headers_single_column():
    entities = build_entities_from_csv_headers(["amount"], "prices.csv", "model", 100)
    assert entities[0]["fields"] == [
        {"name": "amount", "generator": 'randFromCSV("prices.csv", "amount")'}
    ]


def test_build_data_model_content_csv_generators_roundtrip():
    entities = build_entities_from_csv_headers(["city", "zip"], "addresses.csv", "addr", 50)
    result = build_data_model_content("svc", 7, entities)
    reqs = result["entities"]["addr"]["requirements"]
    assert reqs["city"] == 'randFromCSV("addresses.csv", "city")'
    assert reqs["zip"] == 'randFromCSV("addresses.csv", "zip")'
