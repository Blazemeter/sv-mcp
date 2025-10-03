from pydantic import BaseModel, Field

class Service(BaseModel):
    service_id: int = Field(..., description="The unique identifier of the service")
    service_name: str = Field(..., description="The name of the service")
    workspace_id: int = Field(..., description="The unique identifier of the workspace where the service belongs")

    class Config:
        extra = "ignore"  # ignore any additional fields in input dicts
