from __future__ import annotations

from copy import deepcopy
from typing import Any

from common import CONFIG


DEFAULT_OUTPUT_FORMAT = {
    "aspect_ratio": "9:16",
    "orientation": "PORTRAIT",
    "width": 1080,
    "height": 1920,
}


def locked_output_format(config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the deterministic project output format; never make Shot choices."""
    source = (config or CONFIG).get("production_format", DEFAULT_OUTPUT_FORMAT)
    output = {
        "aspect_ratio": source.get("aspect_ratio"),
        "orientation": source.get("orientation"),
        "width": source.get("width"),
        "height": source.get("height"),
    }
    if output != DEFAULT_OUTPUT_FORMAT:
        raise ValueError(
            "CatDrama V4.1 production_format 必须固定为 "
            "9:16 / PORTRAIT / 1080x1920。"
        )
    return deepcopy(output)


def ensure_shot_output_format(
    shot: dict[str, Any],
    *,
    config: dict[str, Any] | None = None,
) -> bool:
    """Migrate an old Shot State or reject a conflicting technical format."""
    expected = locked_output_format(config)
    current = shot.get("output_format")
    if current is None:
        shot["output_format"] = expected
        return True
    if current != expected:
        raise ValueError(
            f"{shot.get('shot_id', 'Shot')} output_format 与项目固定画幅不一致："
            f"{current} != {expected}"
        )
    return False


def portrait_variant_categories(
    config: dict[str, Any] | None = None,
) -> set[str]:
    source = config or CONFIG
    values = source.get(
        "portrait_variant_categories",
        ["cameras", "environments"],
    )
    if not isinstance(values, list) or any(not isinstance(x, str) for x in values):
        raise ValueError("portrait_variant_categories 必须是字符串数组。")
    return {value.strip().lower() for value in values if value.strip()}
