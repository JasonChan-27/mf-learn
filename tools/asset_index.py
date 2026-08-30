from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from common import ASSETS_ROOT, CONFIG, PROJECT_ROOT, normalized_key, project_relative, sha256, slugify


@dataclass(frozen=True)
class AssetRecord:
    id: str
    name: str
    category: str
    path: str
    aliases: list[str]
    tags: list[str]
    sha256: str
    size_bytes: int


def sidecar_path(path: Path) -> Path:
    return path.with_suffix(".asset.json")


def load_sidecar(path: Path) -> dict[str, Any]:
    sidecar = sidecar_path(path)
    if not sidecar.is_file():
        return {}
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"资产元数据 JSON 无效：{sidecar}：{exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"资产元数据必须是对象：{sidecar}")
    return data


def infer_category(path: Path) -> str:
    relative = path.relative_to(ASSETS_ROOT)
    first = relative.parts[0] if relative.parts else "uncategorized"
    return first if first in CONFIG["asset_categories"] else "uncategorized"


def infer_id(path: Path, category: str) -> str:
    relative = path.relative_to(ASSETS_ROOT)
    pieces = [slugify(piece) for piece in relative.with_suffix("").parts[1:]]
    return ".".join([category, *pieces]) if pieces else f"{category}.{slugify(path.stem)}"


def build_record(path: Path) -> AssetRecord:
    meta = load_sidecar(path)
    category = str(meta.get("category") or infer_category(path)).strip().lower()
    asset_id = str(meta.get("id") or infer_id(path, category)).strip()
    name = str(meta.get("name") or path.stem.replace("_", " ").replace("-", " ")).strip()
    aliases = [str(x).strip() for x in meta.get("aliases", []) if str(x).strip()]
    tags = [str(x).strip().lower() for x in meta.get("tags", []) if str(x).strip()]
    # filename and parent folders are always searchable aliases/tags
    aliases = list(dict.fromkeys([name, path.stem, *aliases]))
    tags = list(dict.fromkeys([category, *[slugify(p) for p in path.relative_to(ASSETS_ROOT).parts[:-1]], *tags]))
    return AssetRecord(
        id=asset_id,
        name=name,
        category=category,
        path=project_relative(path),
        aliases=aliases,
        tags=tags,
        sha256=sha256(path),
        size_bytes=path.stat().st_size,
    )


def scan_assets() -> list[AssetRecord]:
    ASSETS_ROOT.mkdir(parents=True, exist_ok=True)
    extensions = {x.lower() for x in CONFIG["asset_extensions"]}
    paths = sorted(
        p for p in ASSETS_ROOT.rglob("*")
        if p.is_file() and p.suffix.lower() in extensions and not p.name.startswith(".")
    )
    records = [build_record(path) for path in paths]
    ids: dict[str, str] = {}
    for record in records:
        if record.id in ids:
            raise ValueError(f"重复资产 ID：{record.id}\n- {ids[record.id]}\n- {record.path}")
        ids[record.id] = record.path
    return records


def registry_payload(records: list[AssetRecord]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "project": CONFIG["project_name"],
        "asset_count": len(records),
        "assets": [asdict(record) for record in records],
    }


def write_registry(output: Path | None = None) -> Path:
    records = scan_assets()
    output = output or ASSETS_ROOT / "AssetRegistry.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(registry_payload(records), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="扫描 Master 资产并生成稳定资产注册表。")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        output = write_registry(args.output)
    except (OSError, ValueError) as exc:
        print(f"资产索引失败：{exc}")
        return 1
    payload = json.loads(output.read_text(encoding="utf-8"))
    print(f"Asset Registry：{output}")
    print(f"已登记资产：{payload['asset_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
