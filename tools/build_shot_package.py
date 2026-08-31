from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

from common import CONFIG, PROJECT_ROOT, sha256
from director_state import (
    read_json,
    sync_scene_index,
    utc_now,
    validate_state_payload,
    write_json,
)
from prompt_contract_qa import validate_compiled_prompt_contract
from image_metadata import image_metadata, require_portrait_image
from production_format import (
    ensure_shot_output_format,
    locked_output_format,
    portrait_variant_categories,
)
from state_prompt_compiler import build_compilation_manifest, compile_prompt_pair


BUILDER_MODE = "DETERMINISTIC_STATE_BUILDER"
PACKAGE_REQUIRED_FILES = [
    "prompt.md",
    "IMAGE_PROMPT.md",
    "VIDEO_PROMPT.md",
    "CHATGPT_HANDOFF.md",
    "PROMPT_COMPILATION_MANIFEST.json",
    "required_assets.json",
    "UPLOAD_MANIFEST.json",
    "PACKAGE_MANIFEST.json",
]


class AssetRequirementError(FileNotFoundError):
    """Expected Runtime blocker: required Master assets are unavailable."""

    def __init__(self, issues: list[dict[str, str]]) -> None:
        self.issues = issues
        summary = ", ".join(item["asset_id"] for item in issues)
        super().__init__(f"缺少或无效的必需 Master 资产：{summary}")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(content)


def _canonical_sha256(payload: Any) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _project_relative(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _resolve_project_path(raw_path: str, project_root: Path) -> Path | None:
    source = Path(raw_path)
    if not source.is_absolute():
        source = project_root / source
    resolved = source.resolve()
    try:
        resolved.relative_to(project_root.resolve())
    except ValueError:
        return None
    return resolved


def _load_asset_registry(project_root: Path) -> dict[str, dict[str, Any]]:
    candidates = [
        project_root / "assets" / "AssetRegistry.json",
        project_root / "assets" / "Asset_Registry.json",
    ]
    registry_path = next((path for path in candidates if path.is_file()), None)
    if registry_path is None:
        return {}

    payload = read_json(registry_path)
    registry: dict[str, dict[str, Any]] = {}
    for record in payload.get("assets", []):
        asset_id = record.get("id")
        if not asset_id:
            raise ValueError(f"Asset Registry 存在无 id 项：{registry_path}")
        if asset_id in registry:
            raise ValueError(f"Asset Registry 存在重复 id：{asset_id}")
        registry[asset_id] = record
    return registry


def _safe_asset_filename(asset_id: str, source: Path) -> str:
    safe_id = re.sub(r"[^\w\u4e00-\u9fff.-]+", "_", asset_id, flags=re.UNICODE)
    safe_id = safe_id.replace(".", "__").strip("_") or "asset"
    suffix = source.suffix.lower() or ".bin"
    return f"{safe_id}{suffix}"


def resolve_assets_detailed(
    asset_ids: list[str],
    *,
    project_root: Path = PROJECT_ROOT,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    registry = _load_asset_registry(project_root)
    variant_categories = portrait_variant_categories(CONFIG)
    resolved: list[dict[str, Any]] = []
    issues: list[dict[str, str]] = []

    for asset_id in asset_ids:
        record = registry.get(asset_id)
        if record is None:
            issues.append({
                "asset_id": asset_id,
                "reason": "NOT_REGISTERED",
                "path": "",
            })
            continue

        raw_path = str(record.get("path", ""))
        source = _resolve_project_path(raw_path, project_root) if raw_path else None
        if source is None:
            issues.append({
                "asset_id": asset_id,
                "reason": "INVALID_REGISTRY_PATH",
                "path": raw_path,
            })
            continue
        if not source.is_file():
            issues.append({
                "asset_id": asset_id,
                "reason": "SOURCE_FILE_MISSING",
                "path": raw_path,
            })
            continue

        actual_size = source.stat().st_size
        expected_size = record.get("size_bytes")
        if expected_size is not None and actual_size != expected_size:
            issues.append({
                "asset_id": asset_id,
                "reason": "SIZE_MISMATCH",
                "path": raw_path,
            })
            continue

        actual_sha256 = sha256(source)
        expected_sha256 = record.get("sha256")
        if expected_sha256 and actual_sha256 != expected_sha256:
            issues.append({
                "asset_id": asset_id,
                "reason": "SHA256_MISMATCH",
                "path": raw_path,
            })
            continue

        canonical_visual = image_metadata(source)
        category = str(
            record.get("category") or asset_id.partition(".")[0]
        ).strip().lower()

        selected_source = source
        selected_path = raw_path
        selected_sha256 = actual_sha256
        selected_size = actual_size
        selected_visual = canonical_visual
        selected_variant: str | None = None
        warnings: list[dict[str, Any]] = []

        registered_variants = record.get("variants") or {}
        if not isinstance(registered_variants, dict):
            issues.append({
                "asset_id": asset_id,
                "reason": "INVALID_VARIANTS_RECORD",
                "path": raw_path,
                "details": "variants 必须是对象",
            })
            continue
        portrait_variant = registered_variants.get("portrait_9x16")
        if category in variant_categories and portrait_variant is not None:
            if not isinstance(portrait_variant, dict):
                issues.append({
                    "asset_id": asset_id,
                    "reason": "INVALID_VARIANT_RECORD",
                    "path": raw_path,
                    "details": "portrait_9x16 必须是 Registry 对象",
                })
                continue
            variant_raw_path = str(portrait_variant.get("path", ""))
            variant_source = (
                _resolve_project_path(variant_raw_path, project_root)
                if variant_raw_path else None
            )
            if variant_source is None:
                issues.append({
                    "asset_id": asset_id,
                    "reason": "INVALID_VARIANT_PATH",
                    "path": variant_raw_path,
                    "details": "portrait_9x16",
                })
                continue
            if not variant_source.is_file():
                issues.append({
                    "asset_id": asset_id,
                    "reason": "VARIANT_SOURCE_MISSING",
                    "path": variant_raw_path,
                    "details": "portrait_9x16",
                })
                continue
            variant_size = variant_source.stat().st_size
            variant_expected_size = portrait_variant.get("size_bytes")
            if (
                variant_expected_size is not None
                and variant_size != variant_expected_size
            ):
                issues.append({
                    "asset_id": asset_id,
                    "reason": "VARIANT_SIZE_MISMATCH",
                    "path": variant_raw_path,
                    "details": "portrait_9x16",
                })
                continue
            variant_sha256 = sha256(variant_source)
            variant_expected_sha256 = portrait_variant.get("sha256")
            if variant_expected_sha256 and variant_sha256 != variant_expected_sha256:
                issues.append({
                    "asset_id": asset_id,
                    "reason": "VARIANT_SHA256_MISMATCH",
                    "path": variant_raw_path,
                    "details": "portrait_9x16",
                })
                continue
            variant_visual = image_metadata(variant_source)
            if variant_visual["orientation"] != "PORTRAIT":
                issues.append({
                    "asset_id": asset_id,
                    "reason": "INVALID_PORTRAIT_VARIANT",
                    "path": variant_raw_path,
                    "details": (
                        f"{variant_visual['width_pixels']}x"
                        f"{variant_visual['height_pixels']} "
                        f"({variant_visual['orientation']})"
                    ),
                })
                continue
            selected_source = variant_source
            selected_path = variant_raw_path
            selected_sha256 = variant_sha256
            selected_size = variant_size
            selected_visual = variant_visual
            selected_variant = "portrait_9x16"
        elif category in variant_categories and canonical_visual["orientation"] != "PORTRAIT":
            dimensions = (
                f"{canonical_visual['width_pixels']}x{canonical_visual['height_pixels']}"
                if canonical_visual["orientation"] is not None
                else "UNKNOWN"
            )
            warnings.append({
                "asset_id": asset_id,
                "reason": "PORTRAIT_VARIANT_RECOMMENDED",
                "blocking": False,
                "canonical_source_path": raw_path,
                "details": (
                    f"{dimensions} ({canonical_visual['orientation'] or 'UNREADABLE'}); "
                    "继续使用 Canonical Master，并由 9:16 Output Contract 重构画面。"
                ),
            })

        resolved.append({
            "asset_id": asset_id,
            "source": selected_source,
            "source_path": _project_relative(selected_source, project_root),
            "source_sha256": selected_sha256,
            "size_bytes": selected_size,
            **selected_visual,
            "source_variant": selected_variant,
            "canonical_source_path": _project_relative(source, project_root),
            "canonical_source_sha256": actual_sha256,
            "canonical_orientation": canonical_visual["orientation"],
            "reference_warnings": warnings,
            "upload_filename": _safe_asset_filename(asset_id, selected_source),
        })

    return resolved, issues


def resolve_assets(
    asset_ids: list[str],
    *,
    project_root: Path = PROJECT_ROOT,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Compatibility API returning unresolved asset IDs as strings."""
    resolved, issues = resolve_assets_detailed(
        asset_ids,
        project_root=project_root,
    )
    return resolved, [item["asset_id"] for item in issues]


def _state_paths(
    episode_dir: Path,
    runtime: dict[str, Any],
) -> tuple[Path, Path]:
    scene_id = runtime["current_scene_id"]
    shot_id = runtime["current_shot_id"]
    scene_dir = episode_dir / "director_state" / scene_id
    shot_path = scene_dir / "shots" / f"{shot_id}_State.json"
    return scene_dir, shot_path


def _previous_shot_id(scene_dir: Path, current_order: int) -> str | None:
    if current_order <= 1:
        return None
    states = []
    for path in (scene_dir / "shots").glob("*_State.json"):
        state = read_json(path)
        states.append((state["order"], state["shot_id"]))
    for order, shot_id in sorted(states):
        if order == current_order - 1:
            return shot_id
    return None


def _previous_final_candidate(
    episode_dir: Path,
    scene_id: str,
    previous_shot_id: str | None,
) -> Path | None:
    if not previous_shot_id:
        return None
    shot_root = episode_dir / "production" / scene_id / previous_shot_id
    candidates = [
        shot_root / f"{previous_shot_id}_Final{suffix}"
        for suffix in [".png", ".jpg", ".jpeg", ".webp"]
    ]
    return next((path for path in candidates if path.is_file()), None)


def build_previous_frame_manifest(
    episode_dir: Path,
    scene_id: str,
    scene_dir: Path,
    shot: dict[str, Any],
    *,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    policy = shot["continuity"]["previous_frame_policy"]
    previous_id = _previous_shot_id(scene_dir, shot["order"])
    final_path = _previous_final_candidate(episode_dir, scene_id, previous_id)
    relative_final = (
        _project_relative(final_path, project_root) if final_path else None
    )

    if policy == "NONE":
        return {
            "policy": policy,
            "previous_shot_id": previous_id,
            "include_previous_final_in_upload": False,
            "previous_final_path": None,
            "instruction": "不上传上一 Shot Final；当前镜头独立建立。",
        }

    if policy == "STATE_REFERENCE_ONLY":
        return {
            "policy": policy,
            "previous_shot_id": previous_id,
            "include_previous_final_in_upload": False,
            "previous_final_path": relative_final,
            "instruction": (
                "只继承上一镜的 Identity / Space / Lighting / Props / Action State。"
                "不上传上一 Final；Camera / Coverage / Composition 以当前 Director Plan 为准。"
            ),
        }

    if policy == "HIGH_PRIORITY_VISUAL_CONTINUITY":
        if not previous_id:
            raise ValueError("HIGH_PRIORITY_VISUAL_CONTINUITY 但不存在上一 Shot。")
        if not final_path:
            raise FileNotFoundError(
                f"{shot['shot_id']} 必须参考 {previous_id} Final，但尚未找到 Final 图片。"
            )
        return {
            "policy": policy,
            "previous_shot_id": previous_id,
            "include_previous_final_in_upload": True,
            "previous_final_path": relative_final,
            "instruction": (
                "上一 Shot Final Frame 是最高优先级连续性参考。"
                "保持 Camera / Composition / Action 连续，只执行当前 Shot Delta。"
            ),
        }

    raise ValueError(f"未知 previous_frame_policy: {policy}")


def _validate_runtime_shot(
    episode_id: str,
    runtime: dict[str, Any],
    scene_state: dict[str, Any],
    shot: dict[str, Any],
) -> None:
    if runtime["next_action"] not in {
        "GENERATE_CURRENT_SHOT_PACKAGE",
        "NEED_ASSET",
    }:
        raise ValueError(
            f"当前 next_action={runtime['next_action']}，不能 Build Shot Package。"
        )
    if not runtime["current_shot_id"]:
        raise ValueError("current_shot_id 为空。")
    if scene_state.get("plan_status") != "LOCKED":
        raise ValueError("当前 Scene Plan 尚未通过 Director QA 并锁定。")
    if shot.get("status") not in {"READY", "PROMPTED"}:
        raise ValueError(
            f"{shot.get('shot_id')} status={shot.get('status')}，不能 Build Shot Package。"
        )

    expected = (
        episode_id,
        runtime["current_scene_id"],
        runtime["current_shot_id"],
    )
    actual = (shot.get("episode_id"), shot.get("scene_id"), shot.get("shot_id"))
    if actual != expected:
        raise ValueError(f"Runtime / Shot State 身份不一致：{actual} != {expected}")
    validate_state_payload(shot, "Shot_State.schema.json")


def _write_asset_requirement(
    episode_id: str,
    runtime: dict[str, Any],
    scene_dir: Path,
    issues: list[dict[str, str]],
) -> Path:
    lines = [
        "# Asset Requirement",
        "",
        f"- Episode: {episode_id}",
        f"- Scene: {runtime['current_scene_id']}",
        f"- Shot: {runtime['current_shot_id']}",
        "",
        "Python 只报告锁定 Shot State 中的资产缺口，不会选择替代 Master。",
        "",
        "## Missing / Invalid Assets",
        "",
    ]
    for issue in issues:
        path_note = f" / `{issue['path']}`" if issue.get("path") else ""
        details_note = f" / {issue['details']}" if issue.get("details") else ""
        lines.append(
            f"- `{issue['asset_id']}` — {issue['reason']}{details_note}{path_note}"
        )
    lines.extend([
        "",
        "补齐对应 Master 文件并重新运行 `python3.12 tools/run.py "
        f"{episode_id}`。",
        "",
    ])
    path = scene_dir / "ASSET_REQUIREMENT.md"
    _write_text(path, "\n".join(lines))
    return path


def _next_package_version(packages_root: Path) -> int:
    versions = []
    if packages_root.is_dir():
        for path in packages_root.iterdir():
            match = re.fullmatch(r"v(\d{3,})", path.name)
            if path.is_dir() and match:
                versions.append(int(match.group(1)))
    return max(versions, default=0) + 1


def _current_package_if_reusable(
    shot_root: Path,
    package_input_sha256: str,
) -> Path | None:
    pointer_path = shot_root / "CURRENT_PACKAGE.json"
    if not pointer_path.is_file():
        return None
    pointer = read_json(pointer_path)
    if pointer.get("package_input_sha256") != package_input_sha256:
        return None
    version = pointer.get("package_version")
    if not isinstance(version, str) or re.fullmatch(r"v\d{3,}", version) is None:
        return None
    package_dir = shot_root / "packages" / version
    if not package_dir.is_dir() or not (package_dir / "upload").is_dir():
        return None
    if any(not (package_dir / name).is_file() for name in PACKAGE_REQUIRED_FILES):
        return None
    manifest = read_json(package_dir / "PACKAGE_MANIFEST.json")
    if manifest.get("package_input_sha256") != package_input_sha256:
        return None
    if manifest.get("output_format") != locked_output_format():
        return None
    for relative_path, expected_sha256 in manifest.get("artifact_sha256", {}).items():
        artifact = package_dir / relative_path
        if not artifact.is_file() or sha256(artifact) != expected_sha256:
            return None
    return package_dir


def refresh_stale_current_package_state(
    episode_id: str,
    episode_dir: Path,
    *,
    project_root: Path = PROJECT_ROOT,
) -> bool:
    """Requeue an unapproved pre-hotfix package without deleting any version."""
    runtime_path = episode_dir / "director_state" / "Runtime_State.json"
    runtime = read_json(runtime_path)
    if runtime.get("next_action") != "WAIT_FOR_IMAGE_APPROVAL":
        return False
    if not runtime.get("current_shot_id"):
        return False

    scene_dir, shot_path = _state_paths(episode_dir, runtime)
    shot = read_json(shot_path)
    if shot.get("approved_image") or shot.get("status") == "IMAGE_APPROVED":
        return False

    expected = locked_output_format()
    pointer_path = (
        episode_dir
        / "production"
        / runtime["current_scene_id"]
        / runtime["current_shot_id"]
        / "CURRENT_PACKAGE.json"
    )
    manifest_format = None
    if pointer_path.is_file():
        pointer = read_json(pointer_path)
        raw_package_dir = pointer.get("package_dir")
        if isinstance(raw_package_dir, str) and raw_package_dir:
            package_dir = _resolve_project_path(raw_package_dir, project_root)
            if package_dir is not None:
                manifest_path = package_dir / "PACKAGE_MANIFEST.json"
                if manifest_path.is_file():
                    manifest_format = read_json(manifest_path).get("output_format")

    if shot.get("output_format") == expected and manifest_format == expected:
        return False

    ensure_shot_output_format(shot)
    shot["status"] = "READY"
    validate_state_payload(shot, "Shot_State.schema.json")

    runtime["scene_status"] = "PRODUCTION"
    runtime["next_action"] = "GENERATE_CURRENT_SHOT_PACKAGE"
    runtime["last_event"] = "STALE_PACKAGE_REQUEUED_FOR_OUTPUT_FORMAT"
    runtime["updated_at"] = utc_now()
    validate_state_payload(runtime, "Runtime_State.schema.json")

    write_json(shot_path, shot)
    write_json(runtime_path, runtime)
    return True


def _prompt_document(prompts: dict[str, str]) -> str:
    return (
        "# Shot Prompt Package\n\n"
        + prompts["handoff"].rstrip()
        + "\n\n---\n\n"
        + prompts["image_prompt"].rstrip()
        + "\n\n---\n\n"
        + prompts["video_prompt"].rstrip()
        + "\n"
    )


def _artifact_hashes(package_dir: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(package_dir.rglob("*")):
        if path.is_file() and path.name != "PACKAGE_MANIFEST.json":
            hashes[path.relative_to(package_dir).as_posix()] = sha256(path)
    return hashes


def _finalize_success_state(
    episode_dir: Path,
    scene_dir: Path,
    shot_path: Path,
    shot: dict[str, Any],
    runtime_path: Path,
    runtime: dict[str, Any],
    previous_frame: dict[str, Any],
    package_filenames: list[str],
    *,
    reused: bool,
) -> None:
    updated_shot = deepcopy(shot)
    updated_shot["status"] = "PROMPTED"
    previous_path = previous_frame.get("previous_final_path")
    updated_shot["continuity"]["previous_frame_filename"] = (
        Path(previous_path).name if previous_path else None
    )
    updated_shot["required_assets"]["package_filenames"] = package_filenames
    validate_state_payload(updated_shot, "Shot_State.schema.json")

    updated_runtime = deepcopy(runtime)
    updated_runtime["scene_status"] = "PRODUCTION"
    updated_runtime["next_action"] = "WAIT_FOR_IMAGE_APPROVAL"
    updated_runtime["last_event"] = (
        "CURRENT_SHOT_PACKAGE_REUSED" if reused else "CURRENT_SHOT_PACKAGE_GENERATED"
    )
    updated_runtime["updated_at"] = utc_now()
    validate_state_payload(updated_runtime, "Runtime_State.schema.json")

    scene_state_path = scene_dir / "Scene_State.json"
    scene_state = read_json(scene_state_path)
    scene_state["status"] = "PRODUCTION"
    scene_state["updated_at"] = utc_now()

    write_json(shot_path, updated_shot)
    write_json(scene_state_path, scene_state)
    sync_scene_index(episode_dir, scene_state)
    write_json(runtime_path, updated_runtime)

    requirement_path = scene_dir / "ASSET_REQUIREMENT.md"
    if requirement_path.is_file():
        requirement_path.unlink()


def build_current_shot_package(
    episode_id: str,
    episode_dir: Path,
    *,
    project_root: Path = PROJECT_ROOT,
) -> Path:
    runtime_path = episode_dir / "director_state" / "Runtime_State.json"
    runtime = read_json(runtime_path)
    scene_dir, shot_path = _state_paths(episode_dir, runtime)
    shot = read_json(shot_path)
    ensure_shot_output_format(shot)
    scene_state = read_json(scene_dir / "Scene_State.json")
    _validate_runtime_shot(episode_id, runtime, scene_state, shot)

    previous_frame = build_previous_frame_manifest(
        episode_dir,
        runtime["current_scene_id"],
        scene_dir,
        shot,
        project_root=project_root,
    )
    prompts = compile_prompt_pair(shot, previous_frame)
    qa_issues = validate_compiled_prompt_contract(
        shot,
        previous_frame,
        prompts["image_prompt"],
        prompts["video_prompt"],
    )
    if qa_issues:
        raise ValueError("Prompt Contract QA Failed:\n- " + "\n- ".join(qa_issues))

    resolved_assets, asset_issues = resolve_assets_detailed(
        shot["required_assets"]["asset_ids"],
        project_root=project_root,
    )
    if asset_issues:
        _write_asset_requirement(episode_id, runtime, scene_dir, asset_issues)
        runtime["scene_status"] = "ASSET_REQUIRED"
        runtime["next_action"] = "NEED_ASSET"
        runtime["last_event"] = "CURRENT_SHOT_ASSET_GAP"
        runtime["updated_at"] = utc_now()
        validate_state_payload(runtime, "Runtime_State.schema.json")
        write_json(runtime_path, runtime)
        raise AssetRequirementError(asset_issues)

    previous_source: Path | None = None
    previous_sha256: str | None = None
    if previous_frame["include_previous_final_in_upload"]:
        previous_source = _resolve_project_path(
            previous_frame["previous_final_path"],
            project_root,
        )
        if previous_source is None or not previous_source.is_file():
            raise FileNotFoundError("Previous Final 路径无效或文件不存在。")
        require_portrait_image(previous_source, "Previous Shot Final")
        previous_sha256 = sha256(previous_source)

    reference_warnings = [
        warning
        for item in resolved_assets
        for warning in item["reference_warnings"]
    ]
    compilation_manifest = build_compilation_manifest(shot, previous_frame, prompts)
    package_input = {
        "builder_mode": BUILDER_MODE,
        "prompt_source_state_sha256": compilation_manifest["source_state_sha256"],
        "output_format": shot["output_format"],
        "assets": [
            {
                "asset_id": item["asset_id"],
                "source_sha256": item["source_sha256"],
                "source_variant": item["source_variant"],
                "upload_filename": item["upload_filename"],
            }
            for item in resolved_assets
        ],
        "previous_final_sha256": previous_sha256,
    }
    package_input_sha256 = _canonical_sha256(package_input)

    shot_root = (
        episode_dir
        / "production"
        / runtime["current_scene_id"]
        / runtime["current_shot_id"]
    )
    reusable = _current_package_if_reusable(shot_root, package_input_sha256)
    if reusable is not None:
        pointer = read_json(shot_root / "CURRENT_PACKAGE.json")
        _finalize_success_state(
            episode_dir,
            scene_dir,
            shot_path,
            shot,
            runtime_path,
            runtime,
            previous_frame,
            pointer.get("package_filenames", []),
            reused=True,
        )
        return reusable

    packages_root = shot_root / "packages"
    packages_root.mkdir(parents=True, exist_ok=True)
    version_number = _next_package_version(packages_root)
    version = f"v{version_number:03d}"
    package_dir = packages_root / version
    staging_dir = Path(tempfile.mkdtemp(prefix=".building-", dir=packages_root))

    try:
        upload_dir = staging_dir / "upload"
        upload_dir.mkdir(parents=True, exist_ok=True)
        _write_text(staging_dir / "prompt.md", _prompt_document(prompts))
        _write_text(staging_dir / "IMAGE_PROMPT.md", prompts["image_prompt"])
        _write_text(staging_dir / "VIDEO_PROMPT.md", prompts["video_prompt"])
        _write_text(staging_dir / "CHATGPT_HANDOFF.md", prompts["handoff"])
        write_json(
            staging_dir / "PROMPT_COMPILATION_MANIFEST.json",
            compilation_manifest,
        )

        upload_items: list[dict[str, Any]] = []
        required_assets: list[dict[str, Any]] = []
        for item in resolved_assets:
            destination = upload_dir / item["upload_filename"]
            shutil.copy2(item["source"], destination)
            upload_items.append({
                "type": "MASTER_ASSET",
                "asset_id": item["asset_id"],
                "source_path": item["source_path"],
                "source_variant": item["source_variant"],
                "canonical_source_path": item["canonical_source_path"],
                "filename": item["upload_filename"],
                "package_path": f"upload/{item['upload_filename']}",
                "source_sha256": item["source_sha256"],
                "priority": "REQUIRED",
            })
            required_assets.append({
                "asset_id": item["asset_id"],
                "source_path": item["source_path"],
                "source_variant": item["source_variant"],
                "canonical_source_path": item["canonical_source_path"],
                "canonical_source_sha256": item["canonical_source_sha256"],
                "canonical_orientation": item["canonical_orientation"],
                "source_sha256": item["source_sha256"],
                "size_bytes": item["size_bytes"],
                "width_pixels": item["width_pixels"],
                "height_pixels": item["height_pixels"],
                "orientation": item["orientation"],
                "upload_path": f"upload/{item['upload_filename']}",
            })

        previous_upload_path = None
        if previous_source is not None:
            previous_filename = previous_source.name
            destination = upload_dir / previous_filename
            shutil.copy2(previous_source, destination)
            previous_upload_path = f"upload/{previous_filename}"
            upload_items.insert(0, {
                "type": "PREVIOUS_FINAL",
                "asset_id": None,
                "source_path": previous_frame["previous_final_path"],
                "filename": previous_filename,
                "package_path": previous_upload_path,
                "source_sha256": previous_sha256,
                "priority": "HIGHEST",
            })

        required_assets_payload = {
            "schema_version": "4.1",
            "episode_id": episode_id,
            "scene_id": runtime["current_scene_id"],
            "shot_id": runtime["current_shot_id"],
            "output_format": shot["output_format"],
            "assets": required_assets,
            "previous_frame": {
                **previous_frame,
                "copied_to_upload": previous_upload_path is not None,
                "upload_path": previous_upload_path,
                "source_sha256": previous_sha256,
            },
            "unresolved_asset_ids": [],
            "reference_warnings": reference_warnings,
            "blocking": False,
        }
        write_json(staging_dir / "required_assets.json", required_assets_payload)

        upload_manifest = {
            "schema_version": "4.1",
            "episode_id": episode_id,
            "scene_id": runtime["current_scene_id"],
            "shot_id": runtime["current_shot_id"],
            "package_version": version,
            "output_format": shot["output_format"],
            "previous_frame": previous_frame,
            "upload_items": upload_items,
            "unresolved_asset_ids": [],
            "reference_warnings": reference_warnings,
            "blocking": False,
            "prompt_contract_qa": {"result": "PASS", "issues": []},
            "rule": (
                "只复制当前 Shot State 声明的 Master；只有 "
                "HIGH_PRIORITY_VISUAL_CONTINUITY 才复制上一 Shot Final。"
            ),
        }
        write_json(staging_dir / "UPLOAD_MANIFEST.json", upload_manifest)

        package_manifest = {
            "schema_version": "4.1",
            "builder_mode": BUILDER_MODE,
            "creative_decision_allowed": False,
            "reads_director_decision": False,
            "state_authority": "Shot_State.json",
            "episode_id": episode_id,
            "scene_id": runtime["current_scene_id"],
            "shot_id": runtime["current_shot_id"],
            "package_version": version,
            "output_format": shot["output_format"],
            "reference_warnings": reference_warnings,
            "package_input_sha256": package_input_sha256,
            "package_input": package_input,
            "artifact_sha256": _artifact_hashes(staging_dir),
            "created_at": utc_now(),
        }
        write_json(staging_dir / "PACKAGE_MANIFEST.json", package_manifest)
        staging_dir.rename(package_dir)
    except Exception:
        if staging_dir.exists():
            shutil.rmtree(staging_dir)
        raise

    package_filenames = [item["filename"] for item in upload_items]
    pointer = {
        "schema_version": "4.1",
        "episode_id": episode_id,
        "scene_id": runtime["current_scene_id"],
        "shot_id": runtime["current_shot_id"],
        "package_version": version,
        "package_dir": _project_relative(package_dir, project_root),
        "package_input_sha256": package_input_sha256,
        "package_filenames": package_filenames,
        "reference_warning_count": len(reference_warnings),
        "updated_at": utc_now(),
    }
    write_json(shot_root / "CURRENT_PACKAGE.json", pointer)
    _finalize_success_state(
        episode_dir,
        scene_dir,
        shot_path,
        shot,
        runtime_path,
        runtime,
        previous_frame,
        package_filenames,
        reused=False,
    )
    return package_dir
