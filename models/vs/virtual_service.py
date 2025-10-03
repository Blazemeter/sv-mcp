from pydantic import BaseModel, Field


class VirtualService(BaseModel):
    virtual_service_id: int = Field("The unique identifier of the virtual service")
    virtual_service_name: str = Field("The name of the virtual service")
    service_id: int = Field("The unique identifier of the service, where virtual services belong to")
    workspace_id: int = Field("The unique identifier of the workspace, where virtual services belong to")
    type: str = Field("Type of the virtual service. Possible values are 'TRANSACTIONAL' and 'MESSAGING'."
                      " Transactional virtual services are used for simulating user interactions with web applications, "
                      " while messaging virtual services are used for simulating message-based interactions.")
    harbor_id: str = Field("BlazeMeter location harbor identifier")
    ship_id: str = Field("BlazeMeter location ship identifier")
    no_matching_request_preference: str = Field("For transactional virtual services, defines the behavior"
                                                " when no matching request is found. Possible values are 'return404' "
                                                "and 'bypasslive'. ")
    endpoint_preference: str = Field(
        "For transactional virtual services, defines endpoint schema. Possible values are 'HTTP' and 'HTTPS'.")
    replicas: int = Field("The number of replicas for the virtual service. Always set to 1 for all virtual services.")

