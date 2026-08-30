"""Compatibility exports for the Phase6 candidate module name.

Phase7's authoritative implementation lives in ``build_shot_package.py``.
"""

from build_shot_package import (
    AssetRequirementError,
    BUILDER_MODE,
    build_current_shot_package,
    build_previous_frame_manifest,
    resolve_assets,
    resolve_assets_detailed,
)


__all__ = [
    "AssetRequirementError",
    "BUILDER_MODE",
    "build_current_shot_package",
    "build_previous_frame_manifest",
    "resolve_assets",
    "resolve_assets_detailed",
]
