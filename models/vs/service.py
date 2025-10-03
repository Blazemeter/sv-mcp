from pydantic import BaseModel, Field


class Service(BaseModel):
    service_id: int = Field("The unique identifier of the service")
    service_name: str = Field("The name of the service")
    workspace_id: int = Field("The unique identifier of the workspace, where service belong to")
