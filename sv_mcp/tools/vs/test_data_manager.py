import csv
import json
import traceback
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

import httpx
from mcp.server.fastmcp import Context

from sv_mcp.config.blazemeter import (
    VS_TOOLS_PREFIX, WORKSPACES_ENDPOINT,
    TDM_PACKAGES_ENDPOINT, TDM_ASSETS_ENDPOINT,
)
from sv_mcp.config.token import BzmToken
from sv_mcp.formatters.test_data import format_tdm_packages, format_tdm_assets
from sv_mcp.models.vs.test_data import TdmAsset
from sv_mcp.models.result import BaseResult
from sv_mcp.telemetry import run_tool
from sv_mcp.tools.utils import tdm_api_request


def build_data_model_content(service_name: str, service_id: int, entities: list) -> dict:
    entities_dict = {}
    for entity in entities:
        entity_name = entity["name"]
        fields = entity["fields"]
        repeat = entity.get("repeat", 1000)
        properties = {f["name"]: {"type": "string"} for f in fields}
        requirements = {f["name"]: f["generator"] for f in fields}
        entities_dict[entity_name] = {
            "title": entity_name,
            "type": "object",
            "properties": properties,
            "requirements": requirements,
            "targets": {
                "defaultCsv": {"type": "csv", "file": "model.csv", "isHeadless": False}
            },
            "datasources": [],
            "repeat": repeat,
        }
    return {
        "schema": "http://blazemeter.com/blazedata/schema",
        "id": str(uuid.uuid4()),
        "title": f"MS-{service_name}-{service_id}",
        "description": "",
        "kind": "sdm",
        "type": "object",
        "entities": entities_dict,
    }


def build_data_model_content_from_csv(
    service_name: str, service_id: int, file_name: str, headers: list,
    field_mappings: Optional[list] = None,
) -> dict:
    stem = Path(file_name).stem
    entity_name = f"{stem}_csv"
    # col_to_field: csv column name → entity field name (default: same)
    col_to_field = {col: col for col in headers}
    if field_mappings:
        for m in field_mappings:
            col_to_field[m["csv_column"]] = m["name"]
    properties = {col_to_field[col]: {"type": "string"} for col in headers}
    requirements = {col_to_field[col]: f'valueOfCSV("{file_name}", "{col}")' for col in headers}
    entities_dict = {
        entity_name: {
            "title": stem,
            "type": "object",
            "properties": properties,
            "requirements": requirements,
            "targets": {entity_name: {"type": "csv", "file": file_name}},
            "datasources": [{"id": {"fileName": file_name}, "type": "csv", "name": file_name, "loop": False}],
        }
    }
    return {
        "schema": "http://blazemeter.com/blazedata/schema",
        "id": str(uuid.uuid4()),
        "title": f"MS-{service_name}-{service_id}",
        "description": "",
        "kind": "sdm",
        "type": "object",
        "entities": entities_dict,
    }


class TestDataManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def _run_tdm_creation(
        self,
        workspace_id: int,
        service_id: int,
        service_name: str,
        data_model_content: dict,
        global_variables: Optional[Dict[str, str]] = None,
    ) -> BaseResult:
        pkg1_name = f"MS-{service_name}-{service_id}"
        pkg2_name = f"MS-service-{service_id}"
        pkg3_name = f"global-entity-{service_id}"

        # 1/7: data-model package
        result = await tdm_api_request(
            self.token, "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{TDM_PACKAGES_ENDPOINT}",
            result_formatter=format_tdm_packages,
            json={"name": pkg1_name, "displayName": pkg1_name, "version": "1.0.0", "dependencies": {}},
        )
        if result.error:
            return result
        package_id_1 = result.result[0].id

        # 2/7: data-model asset — create without data first (asset UUID is unknown until after POST)
        result = await tdm_api_request(
            self.token, "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{TDM_ASSETS_ENDPOINT}",
            json={
                "metadata": {"kind": "sdm", "contentType": "application/json", "fileName": "data-model.json"},
                "packageId": package_id_1,
                "name": pkg1_name,
                "displayName": pkg1_name,
                "type": "data-model",
            },
        )
        if result.error:
            return result
        raw_asset_1 = result.result[0]
        asset_id_1 = raw_asset_1["id"]

        # 3/7: PUT data-model asset with content — id inside content must match asset UUID,
        # content must be a JSON string (not an object)
        data_model_content["id"] = asset_id_1
        result = await tdm_api_request(
            self.token, "PUT",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{TDM_ASSETS_ENDPOINT}/{asset_id_1}",
            result_formatter=format_tdm_assets,
            json={
                **raw_asset_1,
                "data": {
                    "contentType": "application/json",
                    "fileName": "data-model.json",
                    "content": json.dumps(data_model_content),
                },
            },
        )
        if result.error:
            return result

        # 4/7: mock-svc package
        result = await tdm_api_request(
            self.token, "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{TDM_PACKAGES_ENDPOINT}",
            result_formatter=format_tdm_packages,
            json={"name": pkg2_name, "displayName": pkg2_name, "version": "1.0.0", "dependencies": {}},
        )
        if result.error:
            return result
        package_id_2 = result.result[0].id

        # 5/7: mock-svc asset (no data field)
        result = await tdm_api_request(
            self.token, "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{TDM_ASSETS_ENDPOINT}",
            result_formatter=format_tdm_assets,
            json={
                "metadata": {"mock-svc": pkg2_name},
                "packageId": package_id_2,
                "name": pkg2_name,
                "displayName": pkg2_name,
                "type": "mock-svc",
            },
        )
        if result.error:
            return result
        asset_id_2 = result.result[0].id

        # 6/7: global-entity package
        result = await tdm_api_request(
            self.token, "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{TDM_PACKAGES_ENDPOINT}",
            result_formatter=format_tdm_packages,
            json={"name": pkg3_name, "displayName": pkg3_name, "version": "1.0.0", "dependencies": {}},
        )
        if result.error:
            return result
        package_id_3 = result.result[0].id

        # 7/7: global-entity asset
        gv_content = global_variables or {}
        result = await tdm_api_request(
            self.token, "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{TDM_ASSETS_ENDPOINT}",
            result_formatter=format_tdm_assets,
            json={
                "metadata": {"fileName": "global-entity.json", "contentType": "application/json"},
                "packageId": package_id_3,
                "name": pkg3_name,
                "displayName": pkg3_name,
                "type": "global-entity",
                "data": {
                    "fileName": "global-entity.json",
                    "contentType": "application/json",
                    "content": gv_content,
                },
                "dataAccessible": True,
            },
        )
        if result.error:
            return result
        asset_id_3 = result.result[0].id

        # Link dependencies: assetId2 depends on assetId1 (data-model) and assetId3 (global-entity)
        result = await tdm_api_request(
            self.token, "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{TDM_ASSETS_ENDPOINT}/{asset_id_2}/dependencies",
            json=[
                {
                    "id": asset_id_1,
                    "sourceAssetId": asset_id_2,
                    "packageName": pkg1_name,
                    "assetName": pkg1_name,
                    "type": "mock-svc",
                },
                {
                    "id": asset_id_3,
                    "sourceAssetId": asset_id_2,
                    "packageName": pkg3_name,
                    "assetName": pkg3_name,
                    "type": "global-entity-svc",
                },
            ],
        )
        if result.error:
            return result

        return BaseResult(result=[{
            "data_model_package_id": package_id_1,
            "data_model_asset_id": asset_id_1,
            "mock_svc_package_id": package_id_2,
            "mock_svc_asset_id": asset_id_2,
            "global_entity_package_id": package_id_3,
            "global_entity_asset_id": asset_id_3,
        }])

    async def create_from_schema(
        self,
        workspace_id: int,
        service_id: int,
        service_name: str,
        entities: list,
        global_variables: Optional[Dict[str, str]] = None,
    ) -> BaseResult:
        data_model_content = build_data_model_content(service_name, service_id, entities)
        return await self._run_tdm_creation(
            workspace_id, service_id, service_name, data_model_content, global_variables
        )

    async def _upload_csv_file(
        self, workspace_id: int, package_id: str, model_asset_id: str, file_name: str, csv_content: str
    ) -> BaseResult:
        return await tdm_api_request(
            self.token, "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{TDM_ASSETS_ENDPOINT}",
            json={
                "packageId": package_id,
                "name": file_name,
                "type": "data-model-file",
                "data": {
                    "contentType": "text/csv",
                    "fileName": file_name,
                    "content": csv_content,
                },
                "metadata": {
                    "contentType": "text/csv",
                    "fileName": file_name,
                    "modelAssetId": model_asset_id,
                },
            },
        )

    async def create_from_csv(
        self,
        workspace_id: int,
        service_id: int,
        service_name: str,
        csv_file_path: str,
        global_variables: Optional[Dict[str, str]] = None,
    ) -> BaseResult:
        try:
            csv_path = Path(csv_file_path)
            file_name = csv_path.name
            csv_content = csv_path.read_text(encoding="utf-8")
            headers = next(csv.reader(csv_content.splitlines()))
        except Exception as e:
            return BaseResult(error=f"Failed to read {csv_file_path}: {str(e)}")

        data_model_content = build_data_model_content_from_csv(service_name, service_id, file_name, headers)
        result = await self._run_tdm_creation(
            workspace_id, service_id, service_name, data_model_content, global_variables
        )
        if result.error:
            return result

        ids = result.result[0]
        upload_result = await self._upload_csv_file(
            workspace_id, ids["data_model_package_id"], ids["data_model_asset_id"], file_name, csv_content
        )
        if upload_result.error:
            return upload_result

        return result

    async def list(self, workspace_id: int, limit: int = 50, offset: int = 0) -> BaseResult:
        return await tdm_api_request(
            self.token, "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{TDM_ASSETS_ENDPOINT}",
            result_formatter=format_tdm_assets,
            params=[("q", "type=data-model"), ("limit", limit), ("skip", offset)],
        )

    async def read(self, workspace_id: int, service_id: int, service_name: str) -> BaseResult:
        asset_name = f"MS-{service_name}-{service_id}"
        return await tdm_api_request(
            self.token, "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{TDM_ASSETS_ENDPOINT}",
            result_formatter=format_tdm_assets,
            params=[("q", "type=data-model"), ("q", f"name={asset_name}"), ("withData", "true")],
        )

    async def update(
        self,
        workspace_id: int,
        service_id: int,
        service_name: str,
        entities: list,
        global_variables: Optional[Dict[str, str]] = None,
    ) -> BaseResult:
        asset_name = f"MS-{service_name}-{service_id}"
        fetch_result = await tdm_api_request(
            self.token, "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{TDM_ASSETS_ENDPOINT}",
            params=[("q", "type=data-model"), ("q", f"name={asset_name}"), ("withData", "false")],
        )
        if fetch_result.error:
            return fetch_result
        if not fetch_result.result:
            return BaseResult(error=f"No data-model asset found for service_id={service_id} service_name={service_name}. Use create_from_schema to create it first.")

        raw_asset = fetch_result.result[0]
        asset_id = raw_asset["id"]

        data_model_content = build_data_model_content(service_name, service_id, entities)
        data_model_content["id"] = asset_id

        return await tdm_api_request(
            self.token, "PUT",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{TDM_ASSETS_ENDPOINT}/{asset_id}",
            result_formatter=format_tdm_assets,
            json={
                **raw_asset,
                "data": {
                    "contentType": "application/json",
                    "fileName": "data-model.json",
                    "content": json.dumps(data_model_content),
                },
            },
        )

    async def update_from_csv(
        self,
        workspace_id: int,
        service_id: int,
        service_name: str,
        csv_file_path: str,
        field_mappings: Optional[list] = None,
        upload_csv: bool = False,
        global_variables: Optional[Dict[str, str]] = None,
    ) -> BaseResult:
        try:
            csv_path = Path(csv_file_path)
            file_name = csv_path.name
            csv_content = csv_path.read_text(encoding="utf-8")
            headers = next(csv.reader(csv_content.splitlines()))
        except Exception as e:
            return BaseResult(error=f"Failed to read {csv_file_path}: {str(e)}")

        asset_name = f"MS-{service_name}-{service_id}"
        fetch_result = await tdm_api_request(

            self.token, "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{TDM_ASSETS_ENDPOINT}",
            params=[("q", "type=data-model"), ("q", f"name={asset_name}"), ("withData", "false")],
        )
        if fetch_result.error:
            return fetch_result
        if not fetch_result.result:
            return BaseResult(error=f"No data-model asset found for service_id={service_id} service_name={service_name}. Use create_from_csv to create it first.")

        raw_asset = fetch_result.result[0]
        asset_id = raw_asset["id"]

        data_model_content = build_data_model_content_from_csv(
            service_name, service_id, file_name, headers, field_mappings
        )
        data_model_content["id"] = asset_id

        result = await tdm_api_request(
            self.token, "PUT",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{TDM_ASSETS_ENDPOINT}/{asset_id}",
            result_formatter=format_tdm_assets,
            json={
                **raw_asset,
                "data": {
                    "contentType": "application/json",
                    "fileName": "data-model.json",
                    "content": json.dumps(data_model_content),
                },
            },
        )
        if result.error:
            return result

        if upload_csv:
            upload_result = await self._upload_csv_file(
                workspace_id, raw_asset["packageId"], asset_id, file_name, csv_content
            )
            if upload_result.error:
                return upload_result

        return result


def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{VS_TOOLS_PREFIX}_test_data",
        description="""
        Operations on TDM (Test Data Manager) datasets for virtual services.

        Dataset variables are referenced in transaction DSLs using ${fieldName} syntax (not Handlebars).
        Matcher name rules — MUST follow these exactly or matching will fail:
          - URL path with ${fieldName}: matcherName MUST be "equals_url". Never use "matches_url" with variables.
            Example: path "/users/${id}", matcherName "equals_url", matchingValue "/users/${id}"
          - Headers, query params, cookies: matcherName must be "equals" or "equals_insensitive".
            "contains", "matches", "not_matches" do NOT work with dataset variables.
          - Body (plain text): matcherName "equals"
          - Body (JSON): matcherName "equals_json" (variables embedded as JSON values e.g. {"id": "${id}"})
            or "matches_json" with equalTo() helper e.g. [[$.field, equalTo(${id})]]
          - Body (XML): matcherName "equals_xml" or "matches_xml" with matching() helper
          - Response content: base64-encoded string containing ${fieldName} — variables resolve at runtime.
        Additional rules:
          - If the same variable appears multiple times in one transaction (e.g. /test/${id}/${id}?q=${id}),
            ALL occurrences must match the SAME value in the incoming request.
          - Variables not defined in the dataset are treated as literal strings — the request must contain
            the exact text "${varName}" to match.
        Note: Handlebars ({{...}}) is separate — it is for dynamic response templating, not dataset substitution.

        Actions:
        - create_from_schema: Create a dataset by defining entities with field names and generator
            expressions. Supported generators include sequenceGenerator(start), randInt(min,max),
            randText(minLen,maxLen), randDate(min,max), guid(), regExp(pattern), and 80+ others.
            See https://help.blazemeter.com/docs/guide/test-data-generator-functions.html
            args(dict):
                workspace_id (int): Mandatory.
                service_id (int): Mandatory.
                service_name (str): Mandatory. Used in package/asset naming.
                entities (list): Mandatory. Each entry:
                    name (str): entity name.
                    fields (list): each {name: str, generator: str}.
                    repeat (int, default=1000): rows to generate.
                global_variables (dict, optional): flat str→str map of global variables.

        - create_from_csv: Create a dataset from a local CSV file. Column headers become field names;
            the entity name is derived as "{stem}_csv" (e.g. accounts.csv → entity "accounts_csv").
            Generators use valueOfCSV("{filename}", "{field}") — values are sampled from CSV rows at runtime.
            args(dict):
                workspace_id (int): Mandatory.
                service_id (int): Mandatory.
                service_name (str): Mandatory.
                csv_file_path (str): Mandatory. Absolute local path to the CSV file.
                global_variables (dict, optional): flat str→str map of global variables.

        - list: List data-model assets in a workspace (TDM assets endpoint, type=data-model).
            args(dict):
                workspace_id (int): Mandatory.
                limit (int, default=50): max results.
                offset (int, default=0): skip count.

        - read: Read a data-model asset by service. Fetches with full content (withData=true).
            args(dict):
                workspace_id (int): Mandatory.
                service_id (int): Mandatory.
                service_name (str): Mandatory.

        - update: Update an existing schema-based data-model by replacing its entities/fields. Use this
            when the dataset was created with create_from_schema.
            args(dict):
                workspace_id (int): Mandatory.
                service_id (int): Mandatory.
                service_name (str): Mandatory.
                entities (list): Mandatory. Full new entity list (same format as create_from_schema).
                global_variables (dict, optional): flat str→str map of global variables.

        - update_from_csv: Update an existing CSV-based data-model from a local CSV file. Use this
            when the dataset was created with create_from_csv. Rebuilds the entity with valueOfCSV
            generators. Optionally renames entity fields via field_mappings (e.g. when the entity field
            name should differ from the CSV column name).
            By default only the data-model JSON is updated (field rename / mapping change).
            Set upload_csv=true only when the CSV file content itself has changed.
            args(dict):
                workspace_id (int): Mandatory.
                service_id (int): Mandatory.
                service_name (str): Mandatory.
                csv_file_path (str): Mandatory. Absolute local path to the CSV file (used for headers).
                field_mappings (list, optional): rename CSV columns to different entity field names.
                    Each entry: {name: str (entity field name), csv_column: str (CSV column name)}.
                    Example: [{"name": "account_name2", "csv_column": "account_name"}]
                upload_csv (bool, default=false): set true to re-upload the CSV file content.
                global_variables (dict, optional): flat str→str map of global variables.

        TdmAsset Schema:
        """ + str(TdmAsset.model_json_schema())
    )
    async def test_data(action: str, args: Dict[str, Any], ctx: Context) -> BaseResult:
        manager = TestDataManager(token, ctx)

        async def _dispatch():
            match action:
                case "create_from_schema":
                    return await manager.create_from_schema(
                        args["workspace_id"],
                        args["service_id"],
                        args["service_name"],
                        args["entities"],
                        args.get("global_variables"),
                    )
                case "create_from_csv":
                    return await manager.create_from_csv(
                        args["workspace_id"],
                        args["service_id"],
                        args["service_name"],
                        args["csv_file_path"],
                        args.get("global_variables"),
                    )
                case "list":
                    return await manager.list(
                        args["workspace_id"],
                        args.get("limit", 50),
                        args.get("offset", 0),
                    )
                case "read":
                    return await manager.read(
                        args["workspace_id"],
                        args["service_id"],
                        args["service_name"],
                    )
                case "update":
                    return await manager.update(
                        args["workspace_id"],
                        args["service_id"],
                        args["service_name"],
                        args["entities"],
                        args.get("global_variables"),
                    )
                case "update_from_csv":
                    return await manager.update_from_csv(
                        args["workspace_id"],
                        args["service_id"],
                        args["service_name"],
                        args["csv_file_path"],
                        args.get("field_mappings"),
                        args.get("upload_csv", False),
                        args.get("global_variables"),
                    )
                case _:
                    return BaseResult(error=f"Action {action} not found in test_data manager tool")

        try:
            return await run_tool("virtual_services_test_data", action, ctx, _dispatch)
        except httpx.HTTPStatusError:
            return BaseResult(error=f"Error: {traceback.format_exc()}")
        except Exception:
            return BaseResult(
                error=f"""Error: {traceback.format_exc()}
                          If you think this is a bug, please contact BlazeMeter support or report issue at https://github.com/BlazeMeter/bzm-mcp/issues"""
            )
