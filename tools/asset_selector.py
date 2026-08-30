from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, normalized_key

SECTION_MAP = {
    "characters": "characters", "角色": "characters",
    "environments": "environments", "场景": "environments",
    "cameras": "cameras", "机位": "cameras",
    "props": "props", "道具": "props",
    "outfits": "outfits", "服装": "outfits",
}
EMPTY_VALUES = {"", "none", "n/a", "无", "待填写"}
MARKDOWN_ESCAPED_PUNCTUATION = re.compile(r"\\([\\`*_{}\[\]()#+.!|>-])")


@dataclass(frozen=True)
class AssetRequest:
    category: str
    raw: str
    name: str | None = None
    asset_id: str | None = None
    explicit_path: str | None = None


def parse_selection(path: Path) -> list[AssetRequest]:
    if not path.is_file():
        raise FileNotFoundError(f"缺少资产选择文件：{path}")
    current: str | None = None
    requests: list[AssetRequest] = []
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        heading = re.fullmatch(r"##\s+(.+)", line)
        if heading:
            current = SECTION_MAP.get(heading.group(1).strip().casefold())
            continue
        if not current or not line.startswith("-"):
            continue
        value = line[1:].strip().strip("`")
        value = MARKDOWN_ESCAPED_PUNCTUATION.sub(r"\1", value)
        if value.casefold() in EMPTY_VALUES:
            continue
        if value.casefold().startswith("asset:"):
            requests.append(AssetRequest(current, value, asset_id=value.split(":", 1)[1].strip()))
            continue
        parts = [p.strip().strip("`") for p in value.split("|", 1)]
        requests.append(AssetRequest(current, value, name=parts[0], explicit_path=parts[1] if len(parts) == 2 else None))
    return requests


def build_search_index(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        terms = [record["id"], record["name"], Path(record["path"]).stem, *record.get("aliases", [])]
        for term in terms:
            key = normalized_key(str(term))
            if key:
                index.setdefault(key, []).append(record)
    return index


def resolve_requests(requests: list[AssetRequest], records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[dict[str, Any]]]:
    by_id = {r["id"]: r for r in records}
    index = build_search_index(records)
    selected: list[dict[str, Any]] = []
    missing: list[dict[str, str]] = []
    ambiguous: list[dict[str, Any]] = []
    seen: set[str] = set()

    for request in requests:
        matches: list[dict[str, Any]] = []
        reason = ""
        if request.explicit_path:
            candidate = (PROJECT_ROOT / request.explicit_path).resolve()
            for record in records:
                if (PROJECT_ROOT / record["path"]).resolve() == candidate:
                    matches = [record]
                    break
            reason = "explicit_path"
        elif request.asset_id:
            if request.asset_id in by_id:
                matches = [by_id[request.asset_id]]
            reason = "asset_id"
        elif request.name:
            key = normalized_key(request.name)
            matches = [r for r in index.get(key, []) if r["category"] == request.category]
            # exact normalized filename/name may create duplicate references to same record
            matches = list({r["id"]: r for r in matches}.values())
            reason = "name_or_alias"

        if len(matches) == 1:
            record = dict(matches[0])
            if record["id"] not in seen:
                record["selection_reason"] = reason
                selected.append(record)
                seen.add(record["id"])
        elif len(matches) > 1:
            ambiguous.append({"request": request.raw, "category": request.category, "matches": [m["id"] for m in matches]})
        else:
            missing.append({"request": request.raw, "category": request.category})
    return selected, missing, ambiguous
