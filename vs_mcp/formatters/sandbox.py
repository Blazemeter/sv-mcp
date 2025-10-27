from typing import (List, Any, Optional)

from vs_mcp.models.vs.http_header import HttpHeader
from vs_mcp.models.vs.matching_log_entry import MatchingLogEntry
from vs_mcp.models.vs.sandbox import Sandbox
from vs_mcp.models.vs.sandbox_response import SandboxResponse


def format_sandbox_test_request(responses: List[Any], params: Optional[dict] = None) -> List[SandboxResponse]:
    formatted_sandbox_responses = []
    for response in responses:
        formatted_sandbox_responses.append(
            SandboxResponse(
                status=response.get("status"),
                statusMessage=response.get("statusMessage"),
                headers=[HttpHeader(**d) for d in response.get("headers") or []],
                body=response.get("body"),
                matchingLog=[MatchingLogEntry(**d) for d in response.get("matchingLog") or []],
            )
        )
    return formatted_sandbox_responses


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
