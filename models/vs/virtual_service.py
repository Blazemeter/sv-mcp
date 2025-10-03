from pydantic import BaseModel, Field

class VirtualService(BaseModel):
    virtual_service_id: int = Field(..., description="The unique identifier of the virtual service")
    virtual_service_name: str = Field(..., description="The name of the virtual service")
    service_id: int = Field(..., description="The unique identifier of the service where the virtual service belongs")
    workspace_id: int = Field(..., description="The unique identifier of the workspace where the virtual service belongs")
    type: str = Field(
        ...,
        description=(
            "Type of the virtual service. Possible values are 'TRANSACTIONAL' and 'MESSAGING'. "
            "Transactional virtual services are used for simulating user interactions with web applications, "
            "while messaging virtual services are used for simulating message-based interactions."
        )
    )
    harbor_id: str = Field(..., description="BlazeMeter location harbor identifier")
    ship_id: str = Field(..., description="BlazeMeter location ship identifier")
    no_matching_request_preference: str = Field(
        ...,
        description=(
            "For transactional virtual services, defines the behavior when no matching request is found. "
            "Possible values are 'return404' and 'bypasslive'."
        )
    )
    endpoint_preference: str = Field(
        ...,
        description="For transactional virtual services, defines endpoint schema. Possible values are 'HTTP' and 'HTTPS'."
    )
    replicas: int = Field(..., description="The number of replicas for the virtual service. Always set to 1 for all virtual services.")

    class Config:
        extra = "ignore"
