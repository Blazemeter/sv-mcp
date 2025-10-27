from typing import Dict, Any, Optional

from pydantic import BaseModel, Field


class Asset(BaseModel):
    id: int = Field(..., description="The unique identifier of the asset")
    name: str = Field(..., description="The name of the asset")
    type: str = Field(..., description="The type of the asset")
    primaryMetadata: Optional[Dict[str, Any]] = Field(None, description="The asset metadata")

    class Config:
        extra = "ignore"  # ignore any additional fields in input dicts
