from typing import (List, Any, Optional)

from models.vs.generic_dsl import GenericDsl
from models.vs.request_dsl import RequestDsl
from models.vs.transaction import Transaction


def format_transactions(transactions: List[Any], params: Optional[dict] = None) -> List[Transaction]:
    formatted_transactions = []
    for transaction in transactions:
        formatted_transactions.append(
            Transaction(
                transaction_id=transaction.get("id"),
                transaction_name=transaction.get("name"),
                service_id=transaction.get("serviceId"),
                type=transaction.get("type"),
                dsl=GenericDsl(**transaction.get("dsl"))
            )
        )
    return formatted_transactions
