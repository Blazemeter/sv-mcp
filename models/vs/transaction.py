from pydantic import BaseModel, Field

from models.vs.generic_dsl import GenericDsl


class Transaction(BaseModel):
    transaction_id: int = Field("The unique identifier of the transaction")
    transaction_name: str = Field("The name of the transaction")
    service_id: int = Field("The unique identifier of the service, where transactions belong to")
    workspace_id: int = Field("The unique identifier of the workspace, where transactions belong to")
    type: str = Field("Type of the transaction. Possible values are 'HTTP' and 'MESSAGING'."
                      " 'HTTP' transactions are used in 'TRANSACTIONAL' virtual services, 'MESSAGING' transactions"
                      " are used in 'MESSAGING' virtual services.")
    dsl: GenericDsl = Field("Transaction DSL")
