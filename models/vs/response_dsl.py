from typing import Optional

from pydantic import BaseModel, Field

from models.vs.http_header import HttpHeader


class ResponseDsl(BaseModel):
    status: int = Field("Status code of the response for the transaction response matching. E.g. 200, 404.")
    headers: Optional[list[HttpHeader]] = Field("List of response headers")
    content: Optional[str] = Field("Base 64 encoded body of the response")
