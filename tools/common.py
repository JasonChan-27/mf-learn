from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "catdrama.json"


def load_config() -> dict[str, Any]:
    defaults = {
        "project_name": "CatDrama Studio",
        "version": "1.0.0",
        "asset_extensions": [".png", ".jpg", ".jpeg", ".webp", ".pdf"],
        "asset_categories": ["characters", "environments", "cameras", "props", "outfits"],
        "build_directory": "build",
        "strict_by_default": False,
    }
    if CONFIG_PATH.is_file():
        user = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
        defaults.update(user)
    return defaults

CONFIG = load_config()
BUILD_ROOT = PROJECT_ROOT / CONFIG["build_directory"]
ASSETS_ROOT = PROJECT_ROOT / "assets"


def normalize_episode_id(value: str) -> str:
    episode_id = value.strip().upper()
    if not re.fullmatch(r"EP\d{3,}", episode_id):
        raise ValueError("Episode ID 格式错误，请使用 EP001、EP002 等格式。")
    return episode_id


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip().lower()
    value = re.sub(r"[^\w\u4e00-\u9fff]+", "-", value, flags=re.UNICODE)
    return value.strip("-") or "asset"


def normalized_key(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^\w\u4e00-\u9fff]+", "", value, flags=re.UNICODE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_required(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"缺少必需文件：{path}")
    content = path.read_text(encoding="utf-8-sig").strip()
    if not content:
        raise ValueError(f"必需文件为空：{path}")
    return content


def read_optional(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8-sig").strip() or None


def project_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


SCRIPT_NOT_CONFIRMED_MARKER = "<!-- SCRIPT_NOT_CONFIRMED -->"


def confirmed_script_body(path: Path) -> str | None:
    """Return valid confirmed script body, or None while the episode is still in draft."""
    content = read_optional(path)
    if not content or SCRIPT_NOT_CONFIRMED_MARKER in content:
        return None

    content = re.sub(
        r"^\s*#\s*Confirmed\s+Script\s*$",
        "",
        content,
        count=1,
        flags=re.IGNORECASE | re.MULTILINE,
    ).strip()

    invalid_phrases = {
        "not confirmed yet.",
        "script not confirmed.",
        "剧本尚未确认。",
        "尚未确认。",
    }
    if not content or content.casefold() in {x.casefold() for x in invalid_phrases}:
        return None
    return content


def detect_episode_stage(episode_dir: Path) -> str:
    return "production" if confirmed_script_body(episode_dir / "Confirmed_Script.md") else "draft"
