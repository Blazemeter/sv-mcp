from typing import Optional

from pydantic import BaseModel, Field


class ProxyConfiguration(BaseModel):
    proxyUrl: str = Field(..., description="Proxy url")
    nonProxyHosts: Optional[str] = Field(None, description="Non proxy hosts, | separated")
    username: Optional[str] = Field(..., description="Proxy username")
    password: Optional[str] = Field(..., description="Proxy password")
    certificateId: Optional[int] = Field(None, description="Certificate asset identifier")

    class Config:
        extra = "allow"  # allows additional unexpected fields
