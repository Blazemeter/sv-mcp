from pydantic import BaseModel, Field


class Location(BaseModel):
    harborId: str = Field(None, description="Location harbor id")
    shipId: str = Field(None, description="Location ship id")
    shipName: str = Field(None, description="Location name")
    portRange: str = Field(None, description="Location port range")
    kubernetes: bool = Field(None, description="If true - Kubernetes location, if false - Docker location")

    class Config:
        extra = "ignore"  # ignore any additional fields in input dicts
