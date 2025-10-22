from typing import (List, Any, Optional)

from models.vs.generic_dsl import GenericDsl
from models.vs.http_transaction import HttpTransaction
from models.vs.messaging_dsl import MessagingDsl
from models.vs.messaging_transaction import MessagingTransaction


def format_http_transactions(transactions: List[Any], params: Optional[dict] = None) -> List[HttpTransaction]:
    formatted_transactions = []
    for transaction in transactions:
        formatted_transactions.append(
            HttpTransaction(
                id=transaction.get("id"),
                name=transaction.get("name"),
                serviceId=transaction.get("serviceId"),
                type=transaction.get("type"),
                dsl=GenericDsl(**transaction.get("dsl"))
            )
        )
    return formatted_transactions


def format_messaging_transactions(transactions: List[Any], params: Optional[dict] = None) -> List[MessagingTransaction]:
    formatted_transactions = []
    for transaction in transactions:
        formatted_transactions.append(
            MessagingTransaction(
                id=transaction.get("id"),
                name=transaction.get("name"),
                serviceId=transaction.get("serviceId"),
                type=transaction.get("type"),
                dsl=MessagingDsl(**transaction.get("dsl"))
            )
        )
    return formatted_transactions