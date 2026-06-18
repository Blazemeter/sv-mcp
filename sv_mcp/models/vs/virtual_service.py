from typing import Optional, List

from pydantic import BaseModel, Field

from sv_mcp.models.vs.assigned_asset import AssignedAsset
from sv_mcp.models.vs.broker_configuration import BrokerConfiguration
from sv_mcp.models.vs.mock_service_recording import MockServiceRecording
from sv_mcp.models.vs.mock_service_transaction import MockServiceTransaction
from sv_mcp.models.vs.proxy_configuration import ProxyConfiguration
from sv_mcp.models.vs.recorder_config import RecorderConfig
from sv_mcp.models.vs.response_delay import ResponseDelay


class Endpoint(BaseModel):
    endpoint: str = Field(..., description="Endpoint URL")

    class Config:
        extra = "ignore"


class VirtualService(BaseModel):
    id: int = Field(..., description="The unique identifier of the virtual service")
    name: str = Field(..., description="The name of the virtual service")
    status: str = Field("", description="The status of the virtual service")
    serviceId: int = Field(..., description="The unique identifier of the service where the virtual service belongs")
    type: str = Field(
        ...,
        description=(
            "Type of the virtual service. Possible values are 'TRANSACTIONAL' and 'MESSAGING'. "
            "Transactional virtual services are used for simulating user interactions with web applications, "
            "while messaging virtual services are used for simulating message-based interactions."
        )
    )
    harborId: Optional[str] = Field(None, description="Location harbor identifier")
    shipId: Optional[str] = Field(None, description="Location ship identifier")
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
    replicas: int = Field(
        1, description="The number of replicas for the virtual service. Always set to 1."
    )
    mockServiceTransactions: Optional[List[MockServiceTransaction]] = Field(
        [], description="List of transaction definitions associated with the virtual service"
    )
    mockServiceRecordings: Optional[List[MockServiceRecording]] = Field(
        [], description="List of recording references associated with the virtual service"
    )
    endpoints: Optional[List[Endpoint]] = Field(
        [], description="List of virtual service endpoints. Available after deployment only."
    )
    httpRunnerEnabled: bool = Field(
        True,
        description="Http runner enabled flag, must be enabled for virtual services with 'TRANSACTIONAL' type."
    )
    messagingRunnerEnabled: Optional[bool] = Field(
        None, description="Messaging runner enabled flag for 'MESSAGING' type virtual services."
    )
    messagingProtocol: Optional[str] = Field(
        None,
        description=(
            "Messaging broker protocol. One of: IBM_MQ9_JMS, IBM_MQ9_NATIVE, "
            "ACTIVE_MQ_CLASSIC, ACTIVE_MQ_ARTEMIS, KAFKA."
        )
    )
    priorityMode: Optional[str] = Field(
        None, description="Transaction selection mode: DEFAULT or UNIQUE_PRIORITY."
    )
    responseDelay: Optional[ResponseDelay] = Field(
        None, description="Global response delay applied to all transactions in this virtual service."
    )
    recorderConfig: Optional[RecorderConfig] = Field(
        None, description="Configuration for recording live broker traffic."
    )
    classPathJars: Optional[dict] = Field(
        None, description="Custom broker JAR paths, e.g. {\"paths\": [\"string\"]}."
    )
    proxy: Optional[ProxyConfiguration] = Field(None, description="Proxy configuration for the virtual service")
    brokerConfig: Optional[BrokerConfiguration] = Field(
        None, description="Messaging broker connection configuration"
    )
    assets: Optional[List[AssignedAsset]] = Field(None, description="List of assets")

    class Config:
        extra = "ignore"


class ActionResult(BaseModel):
    tracking_id: str = Field(..., description="Action tracking id")

    class Config:
        extra = "ignore"
