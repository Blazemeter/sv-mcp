from pydantic import BaseModel, Field


class QueryParameter(BaseModel):
    name: str = Field(..., description="Query parameter name")
    value: str = Field(..., description="Query parameter value")

    class Config:
        extra = "allow"  # allows additional unexpected fields
