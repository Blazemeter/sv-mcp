from pydantic import BaseModel, Field
from models.vs.generic_dsl import GenericDsl

class Transaction(BaseModel):
    transaction_id: int = Field(..., description="The unique identifier of the transaction")
    transaction_name: str = Field(..., description="The name of the transaction")
    service_id: int = Field(..., description="The unique identifier of the service where the transaction belongs")
    workspace_id: int = Field(..., description="The unique identifier of the workspace where the transaction belongs")
    type: str = Field(
        ...,
        description=(
            "Type of the transaction. Possible values are 'HTTP' and 'MESSAGING'. "
            "'HTTP' transactions are used in 'TRANSACTIONAL' virtual services, "
            "'MESSAGING' transactions are used in 'MESSAGING' virtual services."
        )
    )
    dsl: GenericDsl = Field(..., description="Transaction DSL")

    class Config:
        extra = "ignore"
