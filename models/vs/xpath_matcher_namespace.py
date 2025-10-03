from pydantic import BaseModel, Field


class XmlMatcherNamespace(BaseModel):
    prefix: str = Field("XML namespace prefix.")
    uri: str = Field("XML namespace URI.")
