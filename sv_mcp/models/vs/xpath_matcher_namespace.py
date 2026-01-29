from pydantic import BaseModel, Field

class XmlMatcherNamespace(BaseModel):
    prefix: str = Field(..., description="XML namespace prefix.")
    uri: str = Field(..., description="XML namespace URI.")

    class Config:
        extra = "ignore"
