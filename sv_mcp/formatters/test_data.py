import json
from typing import List, Any, Optional

from sv_mcp.models.vs.test_data import TdmPackage, TdmAsset


def format_tdm_packages(packages: List[Any], params: Optional[dict] = None) -> List[TdmPackage]:
    return [
        TdmPackage(
            id=p.get("id"),
            name=p.get("name"),
            displayName=p.get("displayName"),
            version=p.get("version"),
        )
        for p in packages
    ]


def _parse_asset_content(a: dict) -> Optional[Any]:
    raw = a.get("data") or {}
    content = raw.get("content")
    if not content:
        return None
    if isinstance(content, str):
        try:
            return json.loads(content)
        except (ValueError, TypeError):
            return content
    return content


def format_tdm_assets(assets: List[Any], params: Optional[dict] = None) -> List[TdmAsset]:
    return [
        TdmAsset(
            id=a.get("id"),
            name=a.get("name"),
            displayName=a.get("displayName"),
            type=a.get("type"),
            packageId=a.get("packageId"),
            content=_parse_asset_content(a),
        )
        for a in assets
    ]
