from typing import Optional, List

from pydantic import BaseModel, Field

from sv_mcp.models.vs.assigned_asset import AssignedAsset
from sv_mcp.models.vs.mock_service_transaction import MockServiceTransaction


class VirtualServiceTemplate(BaseModel):
    id: int = Field(..., description="The unique identifier of the virtual service template")
    name: str = Field(..., description="The name of the virtual service template")
    serviceId: int = Field(...,
                           description="The unique identifier of the service where the virtual service template belongs")
    configurationId: Optional[int] = Field(None, description="Configuration identifier")
    noMatchingRequestPreference: str = Field(
        ...,
        description=(
            "Defines the behavior when no matching request is found. "
            "Possible values are 'return404' and 'bypasslive'."
        )
    )
    replicas: int = Field(1,
                          description="The number of replicas for the virtual service template. Always set to 1 for all virtual service templates.")
    mockServiceTransactions: Optional[List[MockServiceTransaction]] = Field(
        [],
        description="List of transaction definitions associated with the virtual service template"
    )
    httpRunnerEnabled: bool = Field(
        True,
        description="Http runner enabled flag, must be enabled for virtual service template"
    )
    assets: Optional[List[AssignedAsset]] = Field(None, description="List of assets")
    class Config:
        extra = "ignore"


class ActionResult(BaseModel):
    tracking_id: str = Field(..., description="Action tracking id")

    class Config:
        extra = "ignore"
