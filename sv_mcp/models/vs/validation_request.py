from pydantic import BaseModel, Field


class ValidationRequest(BaseModel):
    template: str = Field(None, description="Handlebars template to validate")

    class Config:
        extra = "allow"  # allows additional unexpected fields
