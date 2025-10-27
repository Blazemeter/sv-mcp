from pydantic import BaseModel, Field


class ValidationResponse(BaseModel):
    message: str = Field(None, description="Validation result message")
    valid: bool = Field(False, description="Validation result")

    class Config:
        extra = "allow"  # allows additional unexpected fields
