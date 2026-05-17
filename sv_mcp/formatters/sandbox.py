import base64
from typing import List, Any, Optional

from sv_mcp.models.vs.http_header import HttpHeader
from sv_mcp.models.vs.matching_log_entry import MatchingLogEntry
from sv_mcp.models.vs.sandbox import Sandbox
from sv_mcp.models.vs.sandbox_response import SandboxResponse


def format_sandbox_test_request(responses: List[Any], params: Optional[dict] = None) -> List[SandboxResponse]:
    formatted = []
    for response in responses:
        raw_body = response.get("body")
        try:
            body = base64.b64decode(raw_body).decode("utf-8") if raw_body else None
        except (ValueError, UnicodeDecodeError):
            body = raw_body

        formatted.append(
            SandboxResponse(
                status=response.get("status"),
                statusMessage=response.get("statusMessage"),
                headers=[HttpHeader(**d) for d in response.get("headers") or []],
                body=body,
                matchingLog=[MatchingLogEntry(**d) for d in response.get("matchingLog") or []],
            )
        )
    return formatted


def format_sandbox(responses: List[Any], params: Optional[dict] = None) -> List[Sandbox]:
    formatted_sandbox = []
    for response in responses:
        formatted_sandbox.append(
            Sandbox(
                serviceId=response.get("serviceId"),
                userId=response.get("userId"),
                transactionId=response.get("transactionId"),
            )
        )
    return formatted_sandbox
