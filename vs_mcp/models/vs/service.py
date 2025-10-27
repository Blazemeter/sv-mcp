from pydantic import BaseModel, Field

class Service(BaseModel):
    id: int = Field(..., description="The unique identifier of the service")
    name: str = Field(..., description="The name of the service")

    class Config:
        extra = "ignore"  # ignore any additional fields in input dicts
