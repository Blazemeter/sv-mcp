from pydantic import BaseModel, Field


class ConditionMatcher(BaseModel):
    key: str = Field(..., description="Expression to evaluate, in ${...} form, e.g. '${request.query.id}'")
    matcherName: str = Field(..., description="Operator, e.g. 'equals', 'contains', 'matches'")
    matchingValue: str = Field(..., description="Value to compare the expression against")

    class Config:
        extra = "allow"


class ActionCondition(BaseModel):
    matcher: ConditionMatcher = Field(..., description="Condition that must be true for the action to run")

    class Config:
        extra = "allow"
