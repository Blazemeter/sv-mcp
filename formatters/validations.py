from typing import (List, Any, Optional)

from models.vs.service import Service
from models.vs.validation_response import ValidationResponse


def format_validation_request(responses: List[Any], params: Optional[dict] = None) -> List[Service]:
    formatted_responses = []
    for response in responses:
        formatted_responses.append(
            ValidationResponse(
                valid=response.get("valid"),
                message=response.get("message"),
            )
        )
    return formatted_responses
