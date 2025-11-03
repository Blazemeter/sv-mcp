from typing import Optional, List

from pydantic import BaseModel, Field

from vs_mcp.models.vs.mock_service_transaction import MockServiceTransaction
from vs_mcp.models.vs.proxy_configuration import ProxyConfiguration


class Endpoint(BaseModel):
    endpoint: str = Field(..., description="Endpoint URL")

    class Config:
        extra = "ignore"


class VirtualService(BaseModel):
    id: int = Field(..., description="The unique identifier of the virtual service")
    name: str = Field(..., description="The name of the virtual service")
    serviceId: int = Field(..., description="The unique identifier of the service where the virtual service belongs")
    type: str = Field(
        ...,
        description=(
            "Type of the virtual service. Possible values are 'TRANSACTIONAL' and 'MESSAGING'. "
            "Transactional virtual services are used for simulating user interactions with web applications, "
            "while messaging virtual services are used for simulating message-based interactions."
        )
    )
    harborId: str = Field(..., description="Location harbor identifier")
    shipId: str = Field(..., description="Location ship identifier")
    configurationId: Optional[int] = Field(None, description="Configuration identifier")
    noMatchingRequestPreference: str = Field(
        ...,
        description=(
            "For transactional virtual services, defines the behavior when no matching request is found. "
            "Possible values are 'return404' and 'bypasslive'."
        )
    )
    endpointPreference: str = Field(
        ...,
        description="For transactional virtual services, defines endpoint schema. Possible values are 'HTTP' and 'HTTPS'."
    )
    replicas: int = Field(1,
                          description="The number of replicas for the virtual service. Always set to 1 for all virtual services.")
    mockServiceTransactions: Optional[List[MockServiceTransaction]] = Field(
        [],
        description="List of transaction definitions associated with the virtual service"
    )
    endpoints: Optional[List[Endpoint]] = Field(
        [],
        description="List of virtual service endpoints. Available after deployment only."
    )
    httpRunnerEnabled: bool = Field(
        True,
        description="Http runner enabled flag, must be enabled for virtual services with 'TRANSACTIONAL' type."
    )
    proxy: Optional[ProxyConfiguration] = Field(None, description="Proxy configuration for the virtual service")

    class Config:
        extra = "ignore"


class ActionResult(BaseModel):
    tracking_id: str = Field(..., description="Action tracking id")

    class Config:
        extra = "ignore"
