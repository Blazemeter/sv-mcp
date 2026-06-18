import traceback
from typing import Optional, Annotated, Dict, Any, List

import httpx
from mcp.server.fastmcp import Context

from sv_mcp.config.blazemeter import WORKSPACES_ENDPOINT, VS_TOOLS_PREFIX, VS_RECORDINGS_ENDPOINT
from sv_mcp.config.token import BzmToken
from sv_mcp.formatters.recording import format_recordings, format_recorded_messages
from sv_mcp.models.result import BaseResult
from sv_mcp.models.vs.recorded_message import RecordedMessage
from sv_mcp.models.vs.recording import Recording
from sv_mcp.telemetry import run_tool
from sv_mcp.tools.utils import vs_api_request


class RecordingManager:

    def __init__(self, token: Optional[BzmToken], ctx: Context):
        self.token = token
        self.ctx = ctx

    def _recordings_url(self, workspace_id: int) -> str:
        return f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_RECORDINGS_ENDPOINT}"

    def _recording_url(self, workspace_id: int, recording_id: int) -> str:
        return f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_RECORDINGS_ENDPOINT}/{recording_id}"

    def _messages_url(self, workspace_id: int, recording_id: int) -> str:
        return f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_RECORDINGS_ENDPOINT}/{recording_id}/messages"

    def _message_url(self, workspace_id: int, recording_id: int, message_id: int) -> str:
        return f"{WORKSPACES_ENDPOINT}/{workspace_id}/{VS_RECORDINGS_ENDPOINT}/{recording_id}/messages/{message_id}"

    async def list_recordings(
            self,
            workspace_id: int,
            service_id: Optional[int] = None,
            service_mock_id: Optional[int] = None,
            limit: int = 50,
            offset: int = 0,
            fetch_messages: bool = False,
    ) -> BaseResult:
        params: Dict[str, Any] = {"limit": limit, "skip": offset, "fetchMessages": fetch_messages}
        if service_id is not None:
            params["serviceId"] = service_id
        if service_mock_id is not None:
            params["serviceMockId"] = service_mock_id
        return await vs_api_request(
            self.token, "GET", self._recordings_url(workspace_id),
            result_formatter=format_recordings, params=params
        )

    async def read_recording(self, workspace_id: int, recording_id: int) -> BaseResult:
        return await vs_api_request(
            self.token, "GET", self._recording_url(workspace_id, recording_id),
            result_formatter=format_recordings
        )

    async def create_recording(
            self,
            workspace_id: int,
            name: str,
            service_id: Optional[int] = None,
            description: Optional[str] = None,
            tags: Optional[List[str]] = None,
            messages: Optional[List[dict]] = None,
            runtime_config: Optional[dict] = None,
    ) -> BaseResult:
        body: Dict[str, Any] = {"name": name}
        if service_id is not None:
            body["serviceId"] = service_id
        if description is not None:
            body["description"] = description
        if tags is not None:
            body["tags"] = tags
        if messages is not None:
            body["messages"] = messages
        if runtime_config is not None:
            body["runtimeConfig"] = runtime_config
        params: Dict[str, Any] = {}
        if service_id is not None:
            params["serviceId"] = service_id
        return await vs_api_request(
            self.token, "POST", self._recordings_url(workspace_id),
            result_formatter=format_recordings, json=body, params=params
        )

    async def update_recording(
            self,
            workspace_id: int,
            recording_id: int,
            name: str,
            service_id: Optional[int] = None,
            description: Optional[str] = None,
            tags: Optional[List[str]] = None,
            messages: Optional[List[dict]] = None,
            runtime_config: Optional[dict] = None,
    ) -> BaseResult:
        body: Dict[str, Any] = {"name": name}
        if service_id is not None:
            body["serviceId"] = service_id
        if description is not None:
            body["description"] = description
        if tags is not None:
            body["tags"] = tags
        if messages is not None:
            body["messages"] = messages
        if runtime_config is not None:
            body["runtimeConfig"] = runtime_config
        return await vs_api_request(
            self.token, "PUT", self._recording_url(workspace_id, recording_id),
            result_formatter=format_recordings, json=body
        )

    async def patch_recording(
            self,
            workspace_id: int,
            recording_id: int,
            name: Optional[str] = None,
            service_id: Optional[int] = None,
            description: Optional[str] = None,
            tags: Optional[List[str]] = None,
            messages: Optional[List[dict]] = None,
            runtime_config: Optional[dict] = None,
    ) -> BaseResult:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if service_id is not None:
            body["serviceId"] = service_id
        if description is not None:
            body["description"] = description
        if tags is not None:
            body["tags"] = tags
        if messages is not None:
            body["messages"] = messages
        if runtime_config is not None:
            body["runtimeConfig"] = runtime_config
        return await vs_api_request(
            self.token, "PATCH", self._recording_url(workspace_id, recording_id),
            result_formatter=format_recordings, json=body
        )

    async def list_messages(
            self,
            workspace_id: int,
            recording_id: int,
            limit: int = 50,
            offset: int = 0,
    ) -> BaseResult:
        params = {"limit": limit, "skip": offset, "sort": "index"}
        return await vs_api_request(
            self.token, "GET", self._messages_url(workspace_id, recording_id),
            result_formatter=format_recorded_messages, params=params
        )

    async def create_message(
            self,
            workspace_id: int,
            recording_id: int,
            message_type: str,
            content: str,
            destination: str,
            destination_type: str,
            name: Optional[str] = None,
            index: Optional[int] = None,
            delay: Optional[int] = None,
            correlation_id: Optional[str] = None,
            headers: Optional[List[dict]] = None,
            properties: Optional[List[dict]] = None,
            recorded_at: Optional[str] = None,
    ) -> BaseResult:
        body: Dict[str, Any] = {
            "messageType": message_type,
            "content": content,
            "destination": destination,
            "destinationType": destination_type,
        }
        if name is not None:
            body["name"] = name
        if index is not None:
            body["index"] = index
        if delay is not None:
            body["delay"] = delay
        if correlation_id is not None:
            body["correlationId"] = correlation_id
        if headers is not None:
            body["headers"] = headers
        if properties is not None:
            body["properties"] = properties
        if recorded_at is not None:
            body["recordedAt"] = recorded_at
        return await vs_api_request(
            self.token, "POST", self._messages_url(workspace_id, recording_id),
            result_formatter=format_recorded_messages, json=body
        )

    async def update_message(
            self,
            workspace_id: int,
            recording_id: int,
            message_id: int,
            message_type: str,
            content: str,
            destination: str,
            destination_type: str,
            name: Optional[str] = None,
            index: Optional[int] = None,
            delay: Optional[int] = None,
            correlation_id: Optional[str] = None,
            headers: Optional[List[dict]] = None,
            properties: Optional[List[dict]] = None,
            recorded_at: Optional[str] = None,
    ) -> BaseResult:
        body: Dict[str, Any] = {
            "messageType": message_type,
            "content": content,
            "destination": destination,
            "destinationType": destination_type,
        }
        if name is not None:
            body["name"] = name
        if index is not None:
            body["index"] = index
        if delay is not None:
            body["delay"] = delay
        if correlation_id is not None:
            body["correlationId"] = correlation_id
        if headers is not None:
            body["headers"] = headers
        if properties is not None:
            body["properties"] = properties
        if recorded_at is not None:
            body["recordedAt"] = recorded_at
        return await vs_api_request(
            self.token, "PUT", self._message_url(workspace_id, recording_id, message_id),
            result_formatter=format_recorded_messages, json=body
        )

    async def patch_message(
            self,
            workspace_id: int,
            recording_id: int,
            message_id: int,
            message_type: Optional[str] = None,
            content: Optional[str] = None,
            destination: Optional[str] = None,
            destination_type: Optional[str] = None,
            name: Optional[str] = None,
            index: Optional[int] = None,
            delay: Optional[int] = None,
            correlation_id: Optional[str] = None,
            headers: Optional[List[dict]] = None,
            properties: Optional[List[dict]] = None,
            recorded_at: Optional[str] = None,
    ) -> BaseResult:
        body: Dict[str, Any] = {}
        if message_type is not None:
            body["messageType"] = message_type
        if content is not None:
            body["content"] = content
        if destination is not None:
            body["destination"] = destination
        if destination_type is not None:
            body["destinationType"] = destination_type
        if name is not None:
            body["name"] = name
        if index is not None:
            body["index"] = index
        if delay is not None:
            body["delay"] = delay
        if correlation_id is not None:
            body["correlationId"] = correlation_id
        if headers is not None:
            body["headers"] = headers
        if properties is not None:
            body["properties"] = properties
        if recorded_at is not None:
            body["recordedAt"] = recorded_at
        return await vs_api_request(
            self.token, "PATCH", self._message_url(workspace_id, recording_id, message_id),
            result_formatter=format_recorded_messages, json=body
        )


def register(mcp, token: Optional[BzmToken]) -> None:
    @mcp.tool(
        name=f"{VS_TOOLS_PREFIX}_recording",
        description="""
        Operations on recordings and recorded messages within recordings.
        Recordings capture live broker traffic and can be replayed by a messaging virtual service.

        ## Recording actions

        - list_recordings: List recordings in a workspace.
            args:
                workspace_id (int): Mandatory.
                serviceId (int): Optional. Filter by parent service.
                serviceMockId (int): Optional. Filter by virtual service (messaging service mock).
                limit (int, default=50): Max results.
                offset (int, default=0): Pagination offset.
                fetchMessages (bool, default=false): Include inline messages in response.
        - read_recording: Get full details of a recording.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory. Recording ID.
        - create_recording: Create a new recording.
            args:
                workspace_id (int): Mandatory.
                name (str): Mandatory.
                serviceId (int): Optional.
                description (str): Optional.
                tags (list[str]): Optional.
                messages (list): Optional. Inline RecordedMessage objects for seed data.
                runtimeConfig (dict): Optional. {replayCount, delayBetweenReplays, initialDelay}.
        - update_recording: Full replacement of a recording.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
                name (str): Mandatory.
                serviceId (int): Optional.
                description (str): Optional.
                tags (list[str]): Optional.
                messages (list): Optional.
                runtimeConfig (dict): Optional.
        - patch_recording: Partial update — only provided fields are changed.
            args:
                workspace_id (int): Mandatory.
                id (int): Mandatory.
                name (str): Optional.
                serviceId (int): Optional.
                description (str): Optional.
                tags (list[str]): Optional.
                messages (list): Optional.
                runtimeConfig (dict): Optional. {replayCount, delayBetweenReplays, initialDelay}.

        ## Recorded message actions

        content fields are always base64-encoded. Assign sequential index values to control
        playback order; if omitted the server assigns order by insertion sequence.

        Notable JMS headers (use in headers[].name):
          JMS_MESSAGE_ID, JMS_CORRELATION_ID, JMS_TIMESTAMP, JMS_DELIVERY_MODE,
          JMS_REDELIVERED, JMS_EXPIRATION, JMS_PRIORITY
        IBM MQ MQMD headers (IBM MQ protocols only):
          MQ9_MQMD_MsgId, MQ9_MQMD_CorrelId, MQ9_MQMD_Format, MQ9_MQMD_ReplyToQ,
          MQ9_MQMD_ReplyToQMgr, MQ9_MQMD_Persistence, MQ9_MQMD_Priority, MQ9_MQMD_Expiry

        - list_messages: List messages within a recording (sorted by index).
            args:
                workspace_id (int): Mandatory.
                recording_id (int): Mandatory.
                limit (int, default=50): Max results.
                offset (int, default=0): Pagination offset.
        - create_message: Add a recorded message to a recording.
            args:
                workspace_id (int): Mandatory.
                recording_id (int): Mandatory.
                messageType (str): Mandatory. TEXT_MESSAGE | BYTES_MESSAGE | MAP_MESSAGE | STREAM_MESSAGE | OBJECT_MESSAGE.
                content (str): Mandatory. Base64-encoded payload.
                destination (str): Mandatory. Target queue/topic/subscription name.
                destinationType (str): Mandatory. QUEUE | TOPIC | SUBSCRIPTION.
                name (str): Optional.
                index (int): Optional. Sequence position (auto-assigned if omitted).
                delay (int): Optional. Inter-message delay in ms.
                correlationId (str): Optional.
                headers (list): Optional. [{name, value}] JMS/MQMD headers.
                properties (list): Optional. [{name, value, type}] JMS properties.
                recordedAt (str): Optional. ISO-8601 timestamp.
        - update_message: Full replacement of a recorded message.
            args: Same as create_message plus message_id (int): Mandatory.
        - patch_message: Partial update of a recorded message — only provided fields change.
            args:
                workspace_id (int): Mandatory.
                recording_id (int): Mandatory.
                message_id (int): Mandatory.
                messageType (str): Optional.
                content (str): Optional. Base64-encoded.
                destination (str): Optional.
                destinationType (str): Optional.
                name (str): Optional.
                index (int): Optional.
                delay (int): Optional.
                correlationId (str): Optional.
                headers (list): Optional.
                properties (list): Optional.
                recordedAt (str): Optional. ISO-8601 timestamp.

        Recording schema:
        """ + str(Recording.model_json_schema()) + """
        RecordedMessage schema:
        """ + str(RecordedMessage.model_json_schema())
    )
    async def recording(
            action: str,
            args: Annotated[Dict[str, Any], Recording.model_json_schema()],
            ctx: Context,
    ) -> BaseResult:
        mgr = RecordingManager(token, ctx)

        async def _dispatch():
            match action:
                case "list_recordings":
                    return await mgr.list_recordings(
                        workspace_id=args["workspace_id"],
                        service_id=args.get("serviceId"),
                        service_mock_id=args.get("serviceMockId"),
                        limit=args.get("limit", 50),
                        offset=args.get("offset", 0),
                        fetch_messages=args.get("fetchMessages", False),
                    )
                case "read_recording":
                    return await mgr.read_recording(
                        workspace_id=args["workspace_id"],
                        recording_id=args["id"],
                    )
                case "create_recording":
                    return await mgr.create_recording(
                        workspace_id=args["workspace_id"],
                        name=args["name"],
                        service_id=args.get("serviceId"),
                        description=args.get("description"),
                        tags=args.get("tags"),
                        messages=args.get("messages"),
                        runtime_config=args.get("runtimeConfig"),
                    )
                case "update_recording":
                    return await mgr.update_recording(
                        workspace_id=args["workspace_id"],
                        recording_id=args["id"],
                        name=args["name"],
                        service_id=args.get("serviceId"),
                        description=args.get("description"),
                        tags=args.get("tags"),
                        messages=args.get("messages"),
                        runtime_config=args.get("runtimeConfig"),
                    )
                case "patch_recording":
                    return await mgr.patch_recording(
                        workspace_id=args["workspace_id"],
                        recording_id=args["id"],
                        name=args.get("name"),
                        service_id=args.get("serviceId"),
                        description=args.get("description"),
                        tags=args.get("tags"),
                        messages=args.get("messages"),
                        runtime_config=args.get("runtimeConfig"),
                    )
                case "list_messages":
                    return await mgr.list_messages(
                        workspace_id=args["workspace_id"],
                        recording_id=args["recording_id"],
                        limit=args.get("limit", 50),
                        offset=args.get("offset", 0),
                    )
                case "create_message":
                    return await mgr.create_message(
                        workspace_id=args["workspace_id"],
                        recording_id=args["recording_id"],
                        message_type=args["messageType"],
                        content=args["content"],
                        destination=args["destination"],
                        destination_type=args["destinationType"],
                        name=args.get("name"),
                        index=args.get("index"),
                        delay=args.get("delay"),
                        correlation_id=args.get("correlationId"),
                        headers=args.get("headers"),
                        properties=args.get("properties"),
                        recorded_at=args.get("recordedAt"),
                    )
                case "update_message":
                    return await mgr.update_message(
                        workspace_id=args["workspace_id"],
                        recording_id=args["recording_id"],
                        message_id=args["message_id"],
                        message_type=args["messageType"],
                        content=args["content"],
                        destination=args["destination"],
                        destination_type=args["destinationType"],
                        name=args.get("name"),
                        index=args.get("index"),
                        delay=args.get("delay"),
                        correlation_id=args.get("correlationId"),
                        headers=args.get("headers"),
                        properties=args.get("properties"),
                        recorded_at=args.get("recordedAt"),
                    )
                case "patch_message":
                    return await mgr.patch_message(
                        workspace_id=args["workspace_id"],
                        recording_id=args["recording_id"],
                        message_id=args["message_id"],
                        message_type=args.get("messageType"),
                        content=args.get("content"),
                        destination=args.get("destination"),
                        destination_type=args.get("destinationType"),
                        name=args.get("name"),
                        index=args.get("index"),
                        delay=args.get("delay"),
                        correlation_id=args.get("correlationId"),
                        headers=args.get("headers"),
                        properties=args.get("properties"),
                        recorded_at=args.get("recordedAt"),
                    )
                case _:
                    return BaseResult(error=f"Action {action} not found in recording manager tool")

        try:
            return await run_tool("virtual_services_recording", action, ctx, _dispatch)
        except httpx.HTTPStatusError:
            return BaseResult(error=f"Error: {traceback.format_exc()}")
        except Exception:
            return BaseResult(
                error=f"""Error: {traceback.format_exc()}
If you think this is a bug, please contact BlazeMeter support or report issue at https://github.com/BlazeMeter/bzm-mcp/issues"""
            )
