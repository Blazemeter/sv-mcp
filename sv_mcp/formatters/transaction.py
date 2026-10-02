import base64
from typing import (List, Any, Optional)

from sv_mcp.models.vs.assigned_asset import AssignedAsset
from sv_mcp.models.vs.broker_configuration import MessagingTransactionMapping
from sv_mcp.models.vs.generic_dsl import GenericDsl
from sv_mcp.models.vs.http_transaction import HttpTransaction
from sv_mcp.models.vs.messaging_dsl import MessagingDsl
from sv_mcp.models.vs.messaging_transaction import MessagingTransaction


def _decode_body_matcher_value(value: Optional[str]) -> Optional[str]:
    """Backend stores body-matcher matchingValue/sampleBody as base64; decode for display,
    symmetric with HttpTransactionManager.to_base64() applied on create/update."""
    if not value:
        return value
    try:
        return base64.b64decode(value + "=" * (-len(value) % 4), validate=True).decode("utf-8")
    except Exception:
        return value


def format_http_transactions(transactions: List[Any], params: Optional[dict] = None) -> List[HttpTransaction]:
    formatted_transactions = []
    for transaction in transactions:
        dsl_dict = transaction.get("dsl") or {}
        request = dsl_dict.get("requestDsl") or {}
        for body_matcher in request.get("body") or []:
            if "matchingValue" in body_matcher:
                body_matcher["matchingValue"] = _decode_body_matcher_value(body_matcher.get("matchingValue"))
            if "sampleBody" in body_matcher:
                body_matcher["sampleBody"] = _decode_body_matcher_value(body_matcher.get("sampleBody"))
        formatted_transactions.append(
            HttpTransaction(
                id=transaction.get("id"),
                name=transaction.get("name"),
                serviceId=transaction.get("serviceId"),
                type=transaction.get("type"),
                dsl=GenericDsl(**dsl_dict),
                assets=[AssignedAsset(**d) for d in transaction.get("assets") or []],
            )
        )
    return formatted_transactions


def format_messaging_transactions(transactions: List[Any], params: Optional[dict] = None) -> List[MessagingTransaction]:
    formatted_transactions = []
    for transaction in transactions:
        tm_raw = transaction.get("messagingTransactionMappings")
        txn_mapping = MessagingTransactionMapping(**tm_raw) if tm_raw else None
        formatted_transactions.append(
            MessagingTransaction(
                id=transaction.get("id"),
                name=transaction.get("name"),
                serviceId=transaction.get("serviceId"),
                description=transaction.get("description"),
                tags=transaction.get("tags") or [],
                priority=transaction.get("priority"),
                dsl=MessagingDsl(**transaction.get("dsl")),
                messagingTransactionMappings=txn_mapping,
                sampleBody=transaction.get("sampleBody"),
                assets=[AssignedAsset(**d) for d in transaction.get("assets") or []],
            )
        )
    return formatted_transactions
