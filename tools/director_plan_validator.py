from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT
from director_state import read_json
from schema_validator import assert_valid


class DirectorPlanValidationError(ValueError):
    pass


def _nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return len(value) > 0
    return value is not None


def validate_schema(plan: dict[str, Any]) -> None:
    schema_path = PROJECT_ROOT / "director" / "STATE" / "Scene_Director_Plan.schema.json"
    if not schema_path.is_file():
        raise DirectorPlanValidationError(f"Schema 不存在：{schema_path}")

    schema = read_json(schema_path)
    try:
        assert_valid(plan, schema, schema_path.name)
    except ValueError as exc:
        raise DirectorPlanValidationError(f"Schema Validation Failed: {exc}") from exc


def validate_director_plan(plan: dict[str, Any]) -> list[str]:
    validate_schema(plan)
    issues: list[str] = []

    scene_id = plan["scene_id"]
    scene_match = re.search(r"(\d+)$", scene_id)
    scene_num = int(scene_match.group(1)) if scene_match else None
    shots = plan["shots"]
    character_assets = plan["scene_assets"]["character_assets"]

    for idx, shot in enumerate(shots, start=1):
        expected = f"Shot{scene_num:02d}-{idx:02d}" if scene_num is not None else None
        if expected and shot["shot_id"] != expected:
            issues.append(
                f"{shot['shot_id']}: Shot ID 不连续，期望 {expected}"
            )
        if shot["order"] != idx:
            issues.append(
                f"{shot['shot_id']}: order={shot['order']}，期望 {idx}"
            )

        mandatory_creative = [
            "narrative_purpose",
            "audience_feeling",
            "information_gain",
            "why_this_shot",
            "why_not_previous_shot",
            "coverage_reason",
            "composition_intent",
            "camera_reason",
            "camera_motion_reason",
        ]
        for field in mandatory_creative:
            if not _nonempty(shot.get(field)):
                issues.append(f"{shot['shot_id']}: {field} 不能为空")

        fm = shot["frozen_moment"]
        if not fm["physical_boundaries"]:
            issues.append(f"{shot['shot_id']}: physical_boundaries 不能为空")
        if not fm["forbidden_advanced_states"]:
            issues.append(f"{shot['shot_id']}: forbidden_advanced_states 不能为空")

        if shot["camera_status"] == "NEED_NEW_CAMERA":
            issues.append(f"{shot['shot_id']}: NEED_NEW_CAMERA")

        if shot["camera_status"] in {"MATCH", "PARTIAL_MATCH"} and not shot["selected_camera"]:
            issues.append(
                f"{shot['shot_id']}: camera_status={shot['camera_status']} "
                "但 selected_camera 为空"
            )

        if (
            shot["continuity_mode"] == "SAME_CAMERA_CONTINUATION"
            and shot["previous_frame_policy"] != "HIGH_PRIORITY_VISUAL_CONTINUITY"
        ):
            issues.append(
                f"{shot['shot_id']}: SAME_CAMERA_CONTINUATION 必须使用 "
                "HIGH_PRIORITY_VISUAL_CONTINUITY"
            )

        if (
            shot["continuity_mode"] == "CAMERA_CUT_CONTINUITY"
            and shot["previous_frame_policy"] == "HIGH_PRIORITY_VISUAL_CONTINUITY"
        ):
            issues.append(
                f"{shot['shot_id']}: CAMERA_CUT_CONTINUITY 不应使用 "
                "HIGH_PRIORITY_VISUAL_CONTINUITY"
            )

        if idx == 1 and shot["previous_frame_policy"] == "HIGH_PRIORITY_VISUAL_CONTINUITY":
            issues.append(
                f"{shot['shot_id']}: Scene 首镜不能依赖 HIGH_PRIORITY_VISUAL_CONTINUITY"
            )

        for character in dict.fromkeys(
            shot["visible_characters"] + shot["partial_characters"]
        ):
            if character not in character_assets:
                issues.append(
                    f"{shot['shot_id']}: 可见角色 {character} 缺少 "
                    "scene_assets.character_assets 映射"
                )

        if idx < len(shots):
            expected_next = f"Shot{scene_num:02d}-{idx + 1:02d}"
            if shot["next_shot"] != expected_next:
                issues.append(
                    f"{shot['shot_id']}: next_shot={shot['next_shot']}，"
                    f"期望 {expected_next}"
                )

    if not shots[-1]["scene_end"]:
        issues.append("最后一个 Shot 的 scene_end 必须为 true")
    for shot in shots[:-1]:
        if shot["scene_end"]:
            issues.append(f"{shot['shot_id']}: 非最后一镜 scene_end 不能为 true")

    expected_last_next = plan["next_scene"]
    if shots[-1]["next_shot"] != expected_last_next:
        issues.append(
            f"最后一镜 next_shot={shots[-1]['next_shot']}，"
            f"应与 next_scene={expected_last_next} 一致"
        )

    # Micro-action / duplicate visual review gate.
    for previous, current in zip(shots, shots[1:]):
        same_visual = (
            previous["primary_function"] == current["primary_function"]
            and previous["primary_focus"] == current["primary_focus"]
            and previous["coverage"] == current["coverage"]
            and previous["selected_camera"] == current["selected_camera"]
            and previous["information_density"] == current["information_density"]
        )
        if same_visual:
            issues.append(
                f"{previous['shot_id']} → {current['shot_id']}: "
                "Primary Function / Focus / Coverage / Camera / Information Density "
                "全部相同，疑似微动作拆镜；需要 Director Review。"
            )

    return issues


def classify_issues(issues: list[str]) -> str:
    if any("NEED_NEW_CAMERA" in item for item in issues):
        return "NEED_NEW_CAMERA"
    if issues:
        return "REPLAN_REQUIRED"
    return "PASS"
