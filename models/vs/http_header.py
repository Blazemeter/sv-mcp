from pydantic import BaseModel, Field

class HttpHeader(BaseModel):
    name: str = Field("Header name.")
    value: str = Field("Header value.")

