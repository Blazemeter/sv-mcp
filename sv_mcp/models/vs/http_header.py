from pydantic import BaseModel, Field

class HttpHeader(BaseModel):
    name: str = Field(..., description="HTTP header name")
    value: str = Field(..., description="HTTP header value")

    class Config:
        extra = "allow"  # allows additional unexpected fields
