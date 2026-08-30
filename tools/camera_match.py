from __future__ import annotations

import json
import shutil
from copy import deepcopy
from pathlib import Path
from typing import Any

from common import BUILD_ROOT, PROJECT_ROOT
from director_plan_importer import apply_director_plan
from director_state import (
    read_json,
    sync_scene_index,
    utc_now,
    validate_state_payload,
    write_json,
)


def _stored_plan_path(episode_dir: Path, runtime: dict[str, Any]) -> Path:
    scene_dir = episode_dir / "director_state" / runtime["current_scene_id"]
    canonical = scene_dir / "Scene_Director_Plan_RESULT.json"
    if canonical.is_file():
        return canonical

    pending = runtime.get("pending_director_plan")
    if pending:
        candidate = episode_dir / pending
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "Camera Gap 对应的 Scene_Director_Plan_RESULT.json 不存在，"
        "无法只恢复 Camera 匹配。"
    )


def _target_shots(
    plan: dict[str, Any],
    scene_dir: Path,
) -> list[dict[str, Any]]:
    direct = [
        shot for shot in plan["shots"]
        if shot["camera_status"] == "NEED_NEW_CAMERA"
    ]
    if direct:
        return direct

    qa_path = scene_dir / "Director_QA_RESULT.json"
    if not qa_path.is_file():
        return []
    qa = read_json(qa_path)
    if qa.get("result") != "NEED_NEW_CAMERA":
        return []

    requested_ids: list[str] = []
    for issue in qa.get("issues", []):
        for shot_id in issue.get("shot_ids", []):
            if shot_id not in requested_ids:
                requested_ids.append(shot_id)
    by_id = {shot["shot_id"]: shot for shot in plan["shots"]}
    return [by_id[shot_id] for shot_id in requested_ids if shot_id in by_id]


def _camera_candidates(episode_id: str) -> list[dict[str, Any]]:
    selection_path = BUILD_ROOT / episode_id / f"{episode_id}_Asset_Selection.json"
    if not selection_path.is_file():
        raise FileNotFoundError(
            f"缺少最新 Episode Asset Selection：{selection_path}。请先执行 --build。"
        )
    registry_path = PROJECT_ROOT / "assets" / "AssetRegistry.json"
    registry = read_json(registry_path)
    registered = {
        item["id"]: item
        for item in registry.get("assets", [])
        if item.get("category") == "cameras"
    }
    selection = read_json(selection_path)
    candidates: list[dict[str, Any]] = []
    for item in selection.get("selected", []):
        if item.get("category") != "cameras":
            continue
        asset_id = item.get("id")
        if asset_id not in registered:
            continue
        source = registered[asset_id]
        candidates.append({
            "id": asset_id,
            "name": source.get("name", item.get("name", "")),
            "path": source.get("path", item.get("path", "")),
            "aliases": source.get("aliases", []),
            "tags": source.get("tags", []),
            "package_path": item.get("package_path"),
        })
    if not candidates:
        raise ValueError(
            "最新 Asset Selection 中没有已登记的 Camera Master；"
            "请先把新 Camera 加入 Asset_Selection.md 并重新 --build。"
        )
    return candidates


def _target_context(shot: dict[str, Any]) -> dict[str, Any]:
    return {
        "shot_id": shot["shot_id"],
        "narrative_purpose": shot["narrative_purpose"],
        "primary_focus": shot["primary_focus"],
        "coverage": shot["coverage"],
        "coverage_reason": shot["coverage_reason"],
        "composition_intent": shot["composition_intent"],
        "camera_requirement": shot["camera_requirement"],
        "current_selected_camera": shot["selected_camera"],
        "current_camera_status": shot["camera_status"],
        "current_camera_reason": shot["camera_reason"],
        "camera_motion": shot["camera_motion"],
        "camera_motion_reason": shot["camera_motion_reason"],
        "axis_status": shot["axis_status"],
        "continuity_mode": shot["continuity_mode"],
    }


def build_camera_match_files(
    episode_id: str,
    episode_dir: Path,
) -> tuple[Path, Path]:
    state_root = episode_dir / "director_state"
    runtime = read_json(state_root / "Runtime_State.json")
    scene_id = runtime["current_scene_id"]
    scene_dir = state_root / scene_id
    plan_path = _stored_plan_path(episode_dir, runtime)
    plan = read_json(plan_path)
    targets = _target_shots(plan, scene_dir)
    if not targets:
        raise ValueError(
            "当前 Plan / Director QA 没有带明确 Shot ID 的 Camera Gap，"
            "不能进行字段级 Camera Match；需要返回 Scene Planning。"
        )

    candidates = _camera_candidates(episode_id)
    used = {
        shot["selected_camera"]
        for shot in plan["shots"]
        if shot.get("selected_camera")
    }
    candidate_payload = [
        {**item, "currently_used_in_plan": item["id"] in used}
        for item in candidates
    ]
    target_payload = [_target_context(shot) for shot in targets]
    request_data = {
        "source_plan": plan_path.relative_to(PROJECT_ROOT).as_posix(),
        "source_plan_revision": plan["revision"],
        "camera_gap_shots": target_payload,
        "selected_camera_candidates": candidate_payload,
    }
    contract = {
        "schema_version": "4.1",
        "episode_id": episode_id,
        "scene_id": scene_id,
        "source_plan_revision": plan["revision"],
        "resolutions": [
            {
                "shot_id": shot["shot_id"],
                "selected_camera": "",
                "camera_status": "MATCH",
                "camera_reason": "",
            }
            for shot in targets
        ],
    }
    request_text = f"""# {episode_id} {scene_id} — Camera Match Resume Request

当前不是重新规划 Scene。只解决已经锁定的 Director Plan 中的 Camera Gap。

请读取最新 Production Context Package、实际 Camera Master 图片，以及下面的恢复数据。

## 恢复数据

```json
{json.dumps(request_data, ensure_ascii=False, indent=2)}
```

## 导演任务

1. 逐一检查每个 Camera Gap Shot 的叙事目的、Coverage、Composition、Axis、Motion 与 Continuity。
2. 只从 selected_camera_candidates 中选择实际可执行的 Camera Master ID。
3. Camera 选择、MATCH / PARTIAL_MATCH 判定和 camera_reason 必须由 GPT Director 明确决定。
4. 不改变 Shot 数量、顺序、Coverage、Composition、Camera Motion、Axis、Continuity、动作、Frozen Moment 或任何非 Camera 匹配字段。
5. 每个 Camera Gap Shot 必须恰好输出一项 resolution，不得遗漏或增加 Shot。

只输出符合 director/STATE/Camera_Match_Result.schema.json 的纯 JSON；不要 Markdown 代码围栏，不要 IMAGE PROMPT / VIDEO PROMPT，不要内部推理。

输出结构：

```json
{json.dumps(contract, ensure_ascii=False, indent=2)}
```
"""
    request_path = scene_dir / "CAMERA_MATCH_REQUEST.md"
    request_path.write_text(request_text, encoding="utf-8", newline="\n")
    template_path = scene_dir / "Camera_Match_Result_TEMPLATE.json"
    write_json(template_path, contract)
    return request_path, template_path


def _legacy_camera_gap(runtime: dict[str, Any], scene_dir: Path) -> bool:
    if runtime.get("next_action") != "PLAN_CURRENT_SCENE":
        return False
    if runtime.get("last_event") != "CAMERA_LIBRARY_REBUILT_REPLAN_REQUIRED":
        return False
    plan_path = scene_dir / "Scene_Director_Plan_RESULT.json"
    if not plan_path.is_file():
        return False
    plan = read_json(plan_path)
    return any(
        shot.get("camera_status") == "NEED_NEW_CAMERA"
        for shot in plan.get("shots", [])
    )


def resume_camera_gap_after_build(
    episode_id: str,
    episode_dir: Path,
) -> bool:
    state_root = episode_dir / "director_state"
    runtime_path = state_root / "Runtime_State.json"
    runtime = read_json(runtime_path)
    scene_id = runtime["current_scene_id"]
    scene_dir = state_root / scene_id
    if (
        runtime.get("next_action") not in {"NEED_NEW_CAMERA", "CAMERA_MATCH_REQUIRED"}
        and not _legacy_camera_gap(runtime, scene_dir)
    ):
        return False

    request_path, template_path = build_camera_match_files(episode_id, episode_dir)
    plan_path = _stored_plan_path(episode_dir, runtime)
    scene_state_path = scene_dir / "Scene_State.json"
    scene_state = read_json(scene_state_path)
    scene_state["status"] = "CAMERA_REQUIRED"
    scene_state["updated_at"] = utc_now()
    write_json(scene_state_path, scene_state)
    sync_scene_index(episode_dir, scene_state)

    runtime["current_shot_id"] = ""
    runtime["scene_status"] = "CAMERA_REQUIRED"
    runtime["next_action"] = "CAMERA_MATCH_REQUIRED"
    runtime["pending_director_plan"] = plan_path.relative_to(episode_dir).as_posix()
    runtime["pending_camera_match"] = template_path.relative_to(episode_dir).as_posix()
    runtime["last_event"] = "CAMERA_LIBRARY_REBUILT_MATCH_REQUIRED"
    runtime["updated_at"] = utc_now()
    validate_state_payload(runtime, "Runtime_State.schema.json")
    write_json(runtime_path, runtime)
    return request_path.is_file()


def validate_camera_match_result(
    result: dict[str, Any],
    episode_id: str,
    scene_id: str,
    plan: dict[str, Any],
    targets: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> list[str]:
    issues: list[str] = []
    try:
        validate_state_payload(result, "Camera_Match_Result.schema.json")
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        return [str(exc)]

    if result["episode_id"] != episode_id:
        issues.append("episode_id 与当前 Episode 不一致。")
    if result["scene_id"] != scene_id:
        issues.append("scene_id 与当前 Scene 不一致。")
    if result["source_plan_revision"] != plan["revision"]:
        issues.append(
            "source_plan_revision 已过期："
            f"结果为 {result['source_plan_revision']}，当前为 {plan['revision']}。"
        )

    expected = [shot["shot_id"] for shot in targets]
    actual = [item["shot_id"] for item in result["resolutions"]]
    if len(actual) != len(set(actual)):
        issues.append("resolutions 中存在重复 shot_id。")
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        if missing:
            issues.append(f"Camera Gap Shot 未全部处理：{', '.join(missing)}。")
        if extra:
            issues.append(f"resolutions 包含非目标 Shot：{', '.join(extra)}。")

    candidate_ids = {item["id"] for item in candidates}
    for item in result["resolutions"]:
        if item["selected_camera"] not in candidate_ids:
            issues.append(
                f"{item['shot_id']}: selected_camera={item['selected_camera']} "
                "不是当前 Episode Asset Selection 中的 Camera Master。"
            )
    return issues


def apply_camera_match(
    episode_id: str,
    episode_dir: Path,
    result_path: Path,
) -> tuple[str, list[str]]:
    state_root = episode_dir / "director_state"
    runtime_path = state_root / "Runtime_State.json"
    runtime = read_json(runtime_path)
    if runtime.get("next_action") != "CAMERA_MATCH_REQUIRED":
        raise ValueError(
            f"当前 next_action={runtime.get('next_action')}，不能导入 Camera Match。"
        )

    scene_id = runtime["current_scene_id"]
    scene_dir = state_root / scene_id
    plan_path = _stored_plan_path(episode_dir, runtime)
    plan = read_json(plan_path)
    targets = _target_shots(plan, scene_dir)
    candidates = _camera_candidates(episode_id)
    result = read_json(result_path)
    issues = validate_camera_match_result(
        result,
        episode_id,
        scene_id,
        plan,
        targets,
        candidates,
    )
    if issues:
        return "INVALID_CAMERA_MATCH_RESULT", issues

    stored_result = scene_dir / "Camera_Match_Result.json"
    if result_path.resolve() != stored_result.resolve():
        write_json(stored_result, result)

    backup = scene_dir / f"Scene_Director_Plan_PRE_CAMERA_MATCH_R{plan['revision']:03d}.json"
    if not backup.exists():
        shutil.copy2(plan_path, backup)

    patched = deepcopy(plan)
    resolutions = {item["shot_id"]: item for item in result["resolutions"]}
    for shot in patched["shots"]:
        resolution = resolutions.get(shot["shot_id"])
        if resolution is None:
            continue
        shot["selected_camera"] = resolution["selected_camera"]
        shot["camera_status"] = resolution["camera_status"]
        shot["camera_reason"] = resolution["camera_reason"]
    patched["revision"] = plan["revision"] + 1
    write_json(plan_path, patched)

    import_result, import_issues = apply_director_plan(
        episode_id,
        episode_dir,
        plan_path,
        allowed_actions={"CAMERA_MATCH_REQUIRED"},
    )
    updated_runtime = read_json(runtime_path)
    updated_runtime["pending_camera_match"] = stored_result.relative_to(
        episode_dir
    ).as_posix()
    if import_result == "PASS":
        updated_runtime["last_event"] = "CAMERA_MATCH_APPLIED_WAIT_DIRECTOR_QA"
    elif import_result == "NEED_NEW_CAMERA":
        updated_runtime["last_event"] = "CAMERA_MATCH_INCOMPLETE_NEW_CAMERA_REQUIRED"
    else:
        updated_runtime["last_event"] = "CAMERA_MATCH_APPLIED_REPLAN_REQUIRED"
    updated_runtime["updated_at"] = utc_now()
    validate_state_payload(updated_runtime, "Runtime_State.schema.json")
    write_json(runtime_path, updated_runtime)
    return import_result, import_issues
