from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class ServiceDataLinks(BaseModel):
    dataFileLink: Optional[str] = Field(None, description="Link to download the data file of the virtual service")
    previewFileLink: Optional[str] = Field(None, description="Link to download a preview of the data file")
    modelFileLink: Optional[str] = Field(None, description="Link to download the data model the data is generated from")

    class Config:
        extra = "ignore"


class ServiceData(BaseModel):
    links: Optional[ServiceDataLinks] = Field(
        None,
        description="Download links for the service data of the virtual service. Refreshed by the export_data action."
    )
    globalVariables: Dict[str, Any] = Field(
        {},
        description=(
            "Global variables of the virtual service (name to value). These are the global-scope "
            "parameters that STATE_UPDATE 'Update value' and 'Increment value' actions modify. "
            "Transactions read them as ${name}."
        )
    )
    dataSettings: Optional[Any] = Field(None, description="Data settings of the virtual service, as returned by the API")

    class Config:
        extra = "ignore"
