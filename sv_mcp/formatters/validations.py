from typing import (List, Any, Optional)

from sv_mcp.models.vs.validation_response import ValidationResponse


def format_validation_request(responses: List[Any], params: Optional[dict] = None) -> List[ValidationResponse]:
    formatted_responses = []
    for response in responses:
        formatted_responses.append(
            ValidationResponse(
                valid=response.get("valid"),
                message=response.get("message"),
            )
        )
    return formatted_responses
