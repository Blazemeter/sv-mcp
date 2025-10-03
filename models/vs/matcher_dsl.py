from typing import Optional, List

from pydantic import BaseModel, Field

from models.vs.xpath_matcher_namespace import XmlMatcherNamespace


class MatcherDsl(BaseModel):
    key: str = Field("Matcher key. For url matchers has static value 'url', "
                     "for header matchers - header name,"
                     " for body matchers static name 'body',"
                     " for query parameter matchers - query parameter name")
    matcher_name: str = Field("The name of the matcher. "
                              "Supported values for url matchers are: 'matches_url', 'equals_url'. "
                              "Suppoerted values for header, query matchers are: 'equals' - equals matching_value, "
                              "'equals_insensitive' - equals matching_value case insensitive,"
                              " 'contains' - contains matching_value, 'matches' - matches regex expression defined in matching_value,"
                              " 'not_matches' - NOT matches regex expression defined in matching_value, "
                              "'absent' - not present. Supported values for body matchers are: 'equals' - equals matching_value, "
                              "'equals_insensitive' - equals matching_value case insensitive,"
                              " 'contains' - contains matching_value, 'matches' - matches regex expression defined in matching_value,"
                              " 'not_matches' - NOT matches regex expression defined in matching_value, "
                              "'absent' - not present, 'equals_json' - JSON equals matching_value, "
                              "'equals_xml' - XML equals matching_value, 'matches_json' - JSON matches matching_value, "
                              "'matches_xml' - XML matches matching_value, 'matches_xml_schema' - XML matches XML Schema defined in matching_value, "
                              "'matches_xml_cdata' - XML CDATA matches matching_value")
    matching_value: str = Field("Value to match against. Not used for 'absent' matcher_name. If used in body matcher, should be correctly base64 encoded.")
    xml_namespaces: Optional[List[XmlMatcherNamespace]] = Field("Namespaces used for XML matching. Only used if matcher_name is one of 'equals_xml', 'matches_xml', 'matches_xml_schema', 'matches_xml_cdata'")
    c_data_xpath: Optional[str] = Field("CDATA XPath expression used for XML CDATA matching. Only used if matcher_name is 'matches_xml_cdata'")
