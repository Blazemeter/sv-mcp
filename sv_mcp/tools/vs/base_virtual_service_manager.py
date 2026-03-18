import base64
from typing import Optional, List

from mcp.server.fastmcp import Context

from sv_mcp.config.blazemeter import VS_ENDPOINT, WORKSPACES_ENDPOINT
from sv_mcp.config.token import BzmToken
from sv_mcp.formatters.virtual_service import format_virtual_services, format_virtual_services_action
from sv_mcp.models.result import BaseResult
from sv_mcp.tools.utils import vs_api_request


class BaseVirtualServiceManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    async def read(self, workspace_id: int, vs_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services
        )

    async def list(self, workspace_id: int, service_id: Optional[int], limit: int = 50, offset: int = 0) -> BaseResult:
        params = {"limit": limit, "skip": offset}
        if service_id is not None:
            params["serviceId"] = service_id
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}",
            result_formatter=format_virtual_services,
            params=params
        )

    async def deploy(self, workspace_id: int, vs_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}/deploy",
            result_formatter=format_virtual_services_action,
        )

    async def stop(self, workspace_id: int, vs_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}/stop",
            result_formatter=format_virtual_services_action,
        )

    async def configure(self, workspace_id: int, vs_id: int) -> BaseResult:
        return await vs_api_request(
            self.token,
            "GET",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}/configure",
            result_formatter=format_virtual_services_action,
        )

    async def assign_transactions(self, workspace_id: int, vs_id: int, transaction_ids: List[int]) -> BaseResult:
        vs_body = {"includeIds": transaction_ids}
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services,
            json=vs_body,
        )

    async def unassign_transactions(self, workspace_id: int, vs_id: int, transaction_ids: List[int]) -> BaseResult:
        vs_body = {"excludeIds": transaction_ids}
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services,
            json=vs_body,
        )

    async def assign_configuration(self, workspace_id: int, vs_id: int, configuration_id: int) -> BaseResult:
        vs_body = {"configurationId": configuration_id}
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services,
            json=vs_body,
        )

    async def set_proxy(
            self,
            workspace_id: int,
            vs_id: int,
            proxyUrl: str,
            nonProxyHosts: Optional[str],
            username: Optional[str],
            password: Optional[str],
            certificate_id: Optional[int],
    ) -> BaseResult:
        update_request = {"id": vs_id, "workspaceId": workspace_id}
        proxy = {}
        if proxyUrl is not None:
            proxy["proxyUrl"] = proxyUrl
        if nonProxyHosts is not None:
            proxy["nonProxyHosts"] = nonProxyHosts
        if username is not None:
            proxy["username"] = username
        if password is not None:
            proxy["password"] = base64.b64encode(password.encode()).decode()
        if certificate_id is not None:
            assets = []
            assets.append({"assetId": certificate_id, "assetUsageType": "CLIENT_TRUSTSTORE_CERT", "alias": None})
            proxy["assets"] = assets
        update_request["proxy"] = proxy
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services,
            json=update_request,
        )

    async def unset_proxy(
            self,
            workspace_id: int,
            vs_id: int,
    ) -> BaseResult:
        update_request = {"id": vs_id, "workspaceId": workspace_id, "proxy": None}
        return await vs_api_request(
            self.token,
            "PATCH",
            f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_ENDPOINT}/{vs_id}",
            result_formatter=format_virtual_services,
            json=update_request,
        )
