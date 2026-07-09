from pydantic import BaseModel, Field
from typing import Any, Optional


class TdmPackage(BaseModel):
    id: Optional[str] = Field(None, description="Package id (UUID)")
    name: Optional[str] = Field(None, description="Package name")
    displayName: Optional[str] = Field(None, description="Package display name")
    version: Optional[str] = Field(None, description="Package version")

    class Config:
        extra = "allow"


class TdmAsset(BaseModel):
    id: Optional[str] = Field(None, description="Asset id (UUID)")
    name: Optional[str] = Field(None, description="Asset name")
    displayName: Optional[str] = Field(None, description="Asset display name")
    type: Optional[str] = Field(None, description="Asset type: data-model, mock-svc, global-entity")
    packageId: Optional[str] = Field(None, description="Package id this asset belongs to")
    content: Optional[Any] = Field(None, description="Parsed data-model content (present when withData=true)")

    class Config:
        extra = "allow"
