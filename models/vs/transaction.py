from pydantic import BaseModel, Field
from models.vs.generic_dsl import GenericDsl

class Transaction(BaseModel):
    id: int = Field(..., description="The unique identifier of the transaction")
    name: str = Field(..., description="The name of the transaction")
    serviceId: int = Field(..., description="The unique identifier of the service where the transaction belongs")
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
