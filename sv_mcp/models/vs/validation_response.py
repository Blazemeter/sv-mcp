from typing import Optional

from pydantic import BaseModel, Field


class ValidationResponse(BaseModel):
    message: Optional[str] = Field(None, description="Validation result message")
    valid: bool = Field(False, description="Validation result")

    class Config:
        extra = "allow"  # allows additional unexpected fields
