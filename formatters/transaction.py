from typing import (List, Any, Optional)

from models.vs.generic_dsl import GenericDsl
from models.vs.transaction import Transaction


def format_transactions(transactions: List[Any], params: Optional[dict] = None) -> List[Transaction]:
    formatted_transactions = []
    for transaction in transactions:
        formatted_transactions.append(
            Transaction(
                id=transaction.get("id"),
                name=transaction.get("name"),
                serviceId=transaction.get("serviceId"),
                type=transaction.get("type"),
                dsl=GenericDsl(**transaction.get("dsl"))
            )
        )
    return formatted_transactions
