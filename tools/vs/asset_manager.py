import base64
import traceback
from pathlib import Path
from typing import Optional, Dict, Any

import httpx
from mcp.server.fastmcp import Context

from config.blazemeter import VS_ASSETS_ENDPOINT, WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX
from config.token import BzmToken
from formatters.asset import format_assets
from formatters.virtual_service import format_virtual_services_action
from models.result import BaseResult
from models.vs.asset import Asset
from models.vs.virtual_service import ActionResult
from tools.utils import vs_api_request


class AssetManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def read(self, workspace_id: int, asset_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ASSETS_ENDPOINT}/{asset_id}",
            result_formatter=format_assets
        )

    async def list(self, workspace_id: int, limit: int = 50, offset: int = 0) -> BaseResult:
        parameters = {
            "limit": limit,
            "skip": offset
        }

        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ASSETS_ENDPOINT}",
            result_formatter=format_assets,
            params=parameters
        )

    async def set_keystore_passwords(self, workspace_id: int, asset_id: int, keystore_password: str,
                                     key_passwords: Dict[str, str]) -> BaseResult:
        encoded_key_passwords = {}
        if key_passwords is not None:
            encoded_key_passwords = {
                key: {
                    "type": "KEY_PAIR",
                    "password": (
                        base64.b64encode((value if value else "").encode("utf-8")).decode("utf-8")
                    ),
                    "access_granted": False
                }
                for key, value in key_passwords.items()
            }

        metadata = {
            "primaryMetadata": {
                "keystore_password": base64.b64encode(
                    (keystore_password if keystore_password else "").encode("utf-8")).decode("utf-8"),
                "aliases": encoded_key_passwords
            }
        }
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ASSETS_ENDPOINT}/{asset_id}",
            result_formatter=format_assets,
            json=metadata)

    async def upload(self, workspace_id: int, file_path: str) -> BaseResult:
        try:
            file_path_obj = Path(file_path)
            file_name = file_path_obj.name

            with open(file_path, 'rb') as file:
                file_content = file.read()
            files = {
                'file': (file_name, file_content, "text/plain")
            }
            endpoint = f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ASSETS_ENDPOINT}"
            parameters = {
                "type": "CERTIFICATE"
            }
            result = await vs_api_request(
                self.token,
                "POST",
                endpoint,
                params=parameters,
                result_formatter=format_virtual_services_action,
                files=files)
            return result
        except Exception as e:
            raise Exception(f"Failed to upload {file_path}: {str(e)}")


def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{VS_TOOLS_PREFIX}_asset",
        description="""
        Operations on assets. 
        Use this when a user needs to create an asset from file. Supported file extensions: .jks, .keystore, .key, .crt, 
        .cer, .p7b, .p7c, .p7s, .pem
        Actions:
        - read: Reads an Asset. Get the information of an asset.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list asset from.
                asset_id (int): Mandatory. The id of the asset.
        - list: List all assets. 
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list services from.
                limit (int, default=10, valid=[1 to 50]): The number of assets to list.
                offset (int, default=0): Number of assets to skip.
        - set_keystore_passwords: Sets keystore password for the keystore asset.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list asset from.
                asset_id (int): Mandatory. The id of the asset.
                keystore_password (str): Optional. The keystore password.
                key_passwords (dict): Optional. The dictionary of key alias x password.
        - upload: Create a new asset from file.
            Action result contains tracking id to track the create asset process. Use tracking tool to track it.
            Creation of the asset is finished, when tracking status is 'FINISHED'. If creation fails, tracking status is 'FAILED'.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to store the asset.
                file_path (int): Mandatory. The full file path to the file for upload.
        Asset Schema:
        """ + str(Asset.model_json_schema()) + """
        Asset create action result schema:
        """ + str(ActionResult.model_json_schema())
    )
    async def service(action: str, args: Dict[str, Any], ctx: Context) -> BaseResult:
        assert_manager = AssetManager(token, ctx)
        try:
            match action:
                case "read":
                    return await assert_manager.read(args["workspace_id"], args["asset_id"])
                case "list":
                    return await assert_manager.list(args["workspace_id"], args.get("limit", 50),
                                                     args.get("offset", 0))
                case "upload":
                    return await assert_manager.upload(args["workspace_id"], args['file_path'])
                case "set_keystore_passwords":
                    return await assert_manager.set_keystore_passwords(args["workspace_id"], args['asset_id'],
                                                                       args["keystore_password"],
                                                                       args["key_passwords"])
                case _:
                    return BaseResult(
                        error=f"Asset {action} not found in asset manager tool"
                    )
        except httpx.HTTPStatusError:
            return BaseResult(
                error=f"Error: {traceback.format_exc()}"
            )
        except Exception:
            return BaseResult(
                error=f"""Error: {traceback.format_exc()}
                          If you think this is a bug, please contact BlazeMeter support or report issue at https://github.com/BlazeMeter/bzm-mcp/issues"""
            )
