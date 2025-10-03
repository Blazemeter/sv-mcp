from typing import Optional

from pydantic import BaseModel, Field

from models.vs.matcher_dsl import MatcherDsl


class RequestDsl(BaseModel):
    method: str = Field("Http method of the request for the transaction request matching. Uppercase, e.g. 'GET', 'POST'")
    path: str = Field("Path of the request for the transaction request matching. E.g. '/api/v1/resource'. This field is used instead of "
                      "matcher_name for url matcher definition.")
    url: MatcherDsl = Field("Matcher definition for the full URL of the request")
    headers: Optional[list[MatcherDsl]] = Field("List of matchers for the headers of the request")
    query_parameters: Optional[list[MatcherDsl]] = Field("List of matchers for the query parameters of the request")
    body: Optional[MatcherDsl] = Field("Matcher definition for the body of the request")

