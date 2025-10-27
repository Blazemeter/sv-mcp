from typing import (List, Any, Optional)

from vs_mcp.models.vs.asset import Asset


def format_assets(assets: List[Any], params: Optional[dict] = None) -> List[Asset]:
    formatted_assets = []
    for asset in assets:
        formatted_assets.append(
            Asset(
                id=asset.get("id"),
                name=asset.get("name"),
                type=asset.get("type"),
                primaryMetadata=asset.get("primaryMetadata"),
            )
        )
    return formatted_assets
