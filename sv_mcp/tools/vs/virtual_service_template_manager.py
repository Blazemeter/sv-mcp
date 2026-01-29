import traceback
from typing import Optional, Annotated, Dict, Any, List

import httpx
from mcp.server.fastmcp import Context

from sv_mcp.config.blazemeter import VS_TEMPLATE_ENDPOINT, WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX
from sv_mcp.config.token import BzmToken
from sv_mcp.formatters.virtual_service_template import format_virtual_service_templates
from sv_mcp.models.result import BaseResult
from sv_mcp.models.vs.mock_service_transaction import MockServiceTransaction
from sv_mcp.models.vs.virtual_service_template import VirtualServiceTemplate
from sv_mcp.tools.utils import vs_api_request


class VirtualServiceTemplateManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def read(self, workspace_id: int, template_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TEMPLATE_ENDPOINT}/{template_id}",
            result_formatter=format_virtual_service_templates
        )

    async def list(self, workspace_id: int, service_id: Optional[int], limit: int = 50, offset: int = 0) -> BaseResult:
        params = {"limit": limit, "skip": offset}
        if service_id is not None:
            params["serviceId"] = service_id
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TEMPLATE_ENDPOINT}",
            result_formatter=format_virtual_service_templates,
            params=params
        )

    async def create(
            self,
            workspace_id: int,
            vs_name: str,
            service_id: int,
            noMatchingRequestPreference: str,
            mock_service_transactions: List[MockServiceTransaction]
    ) -> BaseResult:
        transactions_list = (
            [txn.model_dump() for txn in mock_service_transactions]
            if isinstance(mock_service_transactions, list)
               and mock_service_transactions
               and isinstance(mock_service_transactions[0], MockServiceTransaction)
            else mock_service_transactions
        )

        template_body = {
            "name": vs_name,
            "serviceId": service_id,
            "replicas": 1,
            "mockServiceTransactions": transactions_list,
            "noMatchingRequestPreference": noMatchingRequestPreference,
            "httpRunnerEnabled": True,
        }

        params = {"serviceId": service_id}
        return await vs_api_request(
            self.token,
            "POST",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TEMPLATE_ENDPOINT}",
            result_formatter=format_virtual_service_templates,
            json=template_body,
            params=params,
        )

    async def update(
            self,
            workspace_id: int,
            template_id: int,
            vs_name: Optional[str],
            service_id: Optional[int],
            noMatchingRequestPreference: Optional[str],
            mock_service_transactions: Optional[List[MockServiceTransaction]],
    ) -> BaseResult:
        update_request = {"id": template_id, "workspaceId": workspace_id}

        if vs_name is not None:
            update_request["name"] = vs_name
        if service_id is not None:
            update_request["serviceId"] = service_id
        if noMatchingRequestPreference is not None:
            update_request["noMatchingRequestPreference"] = noMatchingRequestPreference

        if mock_service_transactions is not None:
            transactions_list = (
                [txn.model_dump() for txn in mock_service_transactions]
                if isinstance(mock_service_transactions, list)
                   and mock_service_transactions
                   and isinstance(mock_service_transactions[0], MockServiceTransaction)
                else mock_service_transactions
            )
            update_request["mockServiceTransactions"] = transactions_list

        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TEMPLATE_ENDPOINT}/{template_id}",
            result_formatter=format_virtual_service_templates,
            json=update_request,
        )

    async def assign_transactions(self, workspace_id: int, template_id: int, transaction_ids: List[int]) -> BaseResult:
        vs_body = {"includeIds": transaction_ids}
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TEMPLATE_ENDPOINT}/{template_id}",
            result_formatter=format_virtual_service_templates,
            json=vs_body,
        )

    async def unassign_transactions(self, workspace_id: int, template_id: int,
                                    transaction_ids: List[int]) -> BaseResult:
        vs_body = {"excludeIds": transaction_ids}
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TEMPLATE_ENDPOINT}/{template_id}",
            result_formatter=format_virtual_service_templates,
            json=vs_body,
        )

    async def assign_configuration(self, workspace_id: int, template_id: int, configuration_id: int) -> BaseResult:
        vs_body = {"configurationId": configuration_id}
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TEMPLATE_ENDPOINT}/{template_id}",
            result_formatter=format_virtual_service_templates,
            json=vs_body,
        )

    async def assign_asset(self, id: int, workspace_id: int, type: str, assetId: int, alias: str) -> BaseResult:
        assert_type_body = {
            "assetId": assetId,
            "usageType": type,
            "alias": alias
        }
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_TEMPLATE_ENDPOINT}/{id}/assign-asset",
            result_formatter=format_virtual_service_templates,
            json=assert_type_body
        )


def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{VS_TOOLS_PREFIX}_virtual_service_template",
        description="""
        Operations on virtual service templates. 
        Virtual service templates can only be used for the HTTP virtual services.
        Actions:
        - read: Read a virtual service template. Get the information of a virtual service template.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list virtual service templates from.
                id (int): Mandatory. The id of the virtual service template to get information.
        - list: List all virtual service templates. 
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace to list transactions from.
                serviceId (int): Optional. The id of the service to list virtual service templates from. 
                Without this it will list all virtual service templates in the workspace.
                limit (int, default=10, valid=[1 to 50]): The number of virtual service templates to list.
                offset (int, default=0): Number of virtual service templates to skip.
        - create: Create a new virtual service template.
            args(VirtualService): A virtual service template object with the following fields:
                workspace_id (int): Mandatory. The id of the workspace.
                name (str): Mandatory. The name of the virtual service template.
                serviceId (int): Mandatory. The id of the service to create the virtual service template in.
                noMatchingRequestPreference (str): Mandatory. If not specified use 'return404'.
        - update: Update an existing new virtual service template.
            args(VirtualService): A virtual service template object with the following fields:
                workspace_id (int): Mandatory. The id of the workspace.
                template_id (int): Mandatory. The id of the virtual service template.
                name (str): Optional. The name of the virtual service template.
                serviceId (int): Optional. The id of the service to create the virtual service template in.
                noMatchingRequestPreference (str): Optional. If not specified use 'return404'.
        - assign_transactions: Assigns the transactions to the virtual service template. 
                Transactions should belong to the same service as the virtual service template.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace the virtual service template belongs to.
                id (int): Mandatory. The id of the virtual service template to assign the transaction to.
                transaction_ids (list[int]): Mandatory. The ids of the transactions to assign to the virtual service template.
        - unassign_transactions: Unassigns the transactions from the virtual service template.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace the virtual service template belongs to.
                id (int): Mandatory. The id of the virtual service template to assign the transaction to.
                transaction_ids (list[int]): Mandatory. The ids of the transactions to unassign from the virtual service template.
        - assign_configuration: Assigns the configuration to the virtual service template. To unassign configuration, assign configuration with id None.
            args(dict): Dictionary with the following required parameters:
                workspace_id (int): Mandatory. The id of the workspace the virtual service template belongs to.
                id (int): Mandatory. The id of the virtual service template to assign the transaction to.
                configuration_id (list[int]): Mandatory. The id of the configuration to assign to the virtual service template.
        - assign_keystore: Assign Keystore asset to the Virtual Service Template.
            args(dict):
                id (int): Mandatory. The id of the Virtual Service Template.
                asset_id (int): Mandatory. The id of the keystore asset to assign.
                alias (str): Mandatory. The certificate alias to use.
                workspace_id (int): Mandatory. The id of the workspace.  
        - assign_keystore_truststore: Assign Keystore asset to the Virtual Service Template. Asset will be used as both Keystore and Truststore.
                Use this action for 2way ssl setup.
            args(dict):
                id (int): Mandatory. The id of the Virtual Service Template.
                asset_id (int): Mandatory. The id of the certificate asset to assign.
                workspace_id (int): Mandatory. The id of the workspace.     
        VirtualServiceTemplate Schema (including full MockServiceTransaction):
        """ + str(VirtualServiceTemplate.model_json_schema())
    )
    async def virtual_service_template(
            action: str,
            args: Annotated[Dict[str, Any], VirtualServiceTemplate.model_json_schema()],
            ctx: Context,
    ) -> BaseResult:
        vs_manager = VirtualServiceTemplateManager(token, ctx)
        try:
            match action:
                case "read":
                    return await vs_manager.read(args["workspace_id"], args["id"])
                case "list":
                    return await vs_manager.list(
                        args["workspace_id"],
                        args.get("serviceId"),
                        args.get("limit", 50),
                        args.get("offset", 0),
                    )
                case "create":
                    return await vs_manager.create(
                        args["workspace_id"],
                        args["name"],
                        args["serviceId"],
                        args.get("noMatchingRequestPreference", "return404"),
                        args.get("mockServiceTransactions", [])
                    )
                case "update":
                    return await vs_manager.update(
                        args["workspace_id"],
                        args["template_id"],
                        args.get("name"),
                        args.get("serviceId"),
                        args.get("noMatchingRequestPreference"),
                        args.get("mockServiceTransactions", [])
                    )
                case "assign_transactions":
                    return await vs_manager.assign_transactions(
                        args["workspace_id"], args["id"], args["transaction_ids"]
                    )
                case "unassign_transactions":
                    return await vs_manager.unassign_transactions(
                        args["workspace_id"], args["id"], args["transaction_ids"]
                    )
                case "assign_configuration":
                    return await vs_manager.assign_configuration(
                        args["workspace_id"], args["id"], args["configuration_id"]
                    )
                case "assign_keystore_truststore":
                    return await vs_manager.assign_asset(
                        args["id"],
                        args["workspace_id"],
                        "SERVER_KEYSTORE_TRUSTSTORE",
                        args["asset_id"],
                        args["alias"],
                    )
                case "assign_keystore":
                    return await vs_manager.assign_asset(
                        args["id"],
                        args["workspace_id"],
                        "SERVER_KEYSTORE",
                        args["asset_id"],
                        None,
                    )
                case _:
                    return BaseResult(error=f"Action {action} not found in virtual service template manager tool")
        except httpx.HTTPStatusError:
            return BaseResult(error=f"Error: {traceback.format_exc()}")
        except Exception:
            return BaseResult(
                error=f"""Error: {traceback.format_exc()}
If you think this is a bug, please contact BlazeMeter support or report issue at https://github.com/BlazeMeter/bzm-mcp/issues"""
            )
