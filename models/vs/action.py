from pydantic import BaseModel, Field


class Action(BaseModel):
    name: str = Field(..., description="Action name")

    class Config:
        extra = "ignore"  # ignore any additional fields in input dicts
