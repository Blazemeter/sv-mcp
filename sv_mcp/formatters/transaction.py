from typing import (List, Any, Optional)

from sv_mcp.models.vs.assigned_asset import AssignedAsset
from sv_mcp.models.vs.generic_dsl import GenericDsl
from sv_mcp.models.vs.http_transaction import HttpTransaction
from sv_mcp.models.vs.messaging_dsl import MessagingDsl
from sv_mcp.models.vs.messaging_transaction import MessagingTransaction


def format_http_transactions(transactions: List[Any], params: Optional[dict] = None) -> List[HttpTransaction]:
    formatted_transactions = []
    for transaction in transactions:
        formatted_transactions.append(
            HttpTransaction(
                id=transaction.get("id"),
                name=transaction.get("name"),
                serviceId=transaction.get("serviceId"),
                type=transaction.get("type"),
                dsl=GenericDsl(**transaction.get("dsl")),
                assets=[AssignedAsset(**d) for d in transaction.get("assets") or []],
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
                dsl=MessagingDsl(**transaction.get("dsl")),
                assets=[AssignedAsset(**d) for d in transaction.get("assets") or []],
            )
        )
    return formatted_transactions