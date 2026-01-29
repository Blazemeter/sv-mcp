from typing import Optional, Dict

from pydantic import BaseModel, Field


class Configuration(BaseModel):
    id: Optional[int] = Field(None, description="Configuration id")
    name: str = Field(..., description="Configuration parameter name")
    description: Optional[str] = Field(None, description="Configuration parameter name")
    configurationMap: Optional[Dict[str, str]] = Field(..., description="Configuration map")

    class Config:
        extra = "allow"  # allows additional unexpected fields
