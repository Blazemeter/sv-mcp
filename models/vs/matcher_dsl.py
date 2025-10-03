from typing import Optional, List
from pydantic import BaseModel, Field
from models.vs.xpath_matcher_namespace import XmlMatcherNamespace

class MatcherDsl(BaseModel):
    key: str = Field(
        ...,
        description=(
            "Matcher key. For URL matchers has static value 'url', "
            "for header matchers - header name, "
            "for body matchers static name 'body', "
            "for query parameter matchers - query parameter name"
        )
    )
    matcherName: str = Field(
        ...,
        description=(
            "The name of the matcher. Supported values for URL matchers: 'matches_url', 'equals_url'. "
            "Supported values for header/query matchers: 'equals', 'equals_insensitive', 'contains', 'matches', 'not_matches', 'absent'. "
            "Supported values for body matchers: 'equals', 'equals_insensitive', 'contains', 'matches', 'not_matches', 'absent', "
            "'equals_json', 'equals_xml', 'matches_json', 'matches_xml', 'matches_xml_schema', 'matches_xml_cdata'."
        )
    )
    matchingValue: str = Field(
        ...,
        description=(
            "Value to match against. Not used for 'absent' matcher_name. "
            "If used in body matcher, should be correctly base64 encoded."
        )
    )
    optional: bool = Field(
        ...,
        description="If true, the matcher is optional and does not need to be present to match."
    )
    namespaces: Optional[List[XmlMatcherNamespace]] = Field(
        None,
        description=(
            "Namespaces used for XML matching. Only used if matcher_name is one of "
            "'equals_xml', 'matches_xml', 'matches_xml_schema', 'matches_xml_cdata'."
        )
    )
    cdataXpath: Optional[str] = Field(
        None,
        description="CDATA XPath expression used for XML CDATA matching. Only used if matcher_name is 'matches_xml_cdata'."
    )

    class Config:
        extra = "allow"
