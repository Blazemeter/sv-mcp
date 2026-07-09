from typing import Optional
from pydantic import BaseModel, Field


class ResponseDelay(BaseModel):
    type: str = Field("FIXED", description="Delay type: FIXED, LOGNORMAL, or UNIFORM")
    fixedDelay: Optional[int] = Field(None, description="Fixed delay in ms (FIXED type)")
    median: Optional[float] = Field(None, description="Median for LOGNORMAL distribution")
    sigma: Optional[float] = Field(None, description="Sigma for LOGNORMAL distribution")
    lower: Optional[float] = Field(None, description="Lower bound for UNIFORM distribution")
    upper: Optional[float] = Field(None, description="Upper bound for UNIFORM distribution")

    class Config:
        extra = "allow"
