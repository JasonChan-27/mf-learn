from __future__ import annotations

import shutil
from pathlib import Path

from director_plan_compiler import compile_plan_to_state
from director_plan_validator import (
    classify_issues,
    validate_director_plan,
)
from director_state import (
    read_json,
    sync_scene_index,
    utc_now,
    validate_state_payload,
    write_json,
)


def _write_camera_requirement(scene_dir: Path, plan: dict) -> Path:
    lines = [
        "# Camera Requirement",
        "",
        f"- Episode: {plan['episode_id']}",
        f"- Scene: {plan['scene_id']}",
        "",
        "Python 只记录 GPT Director 声明的 Camera Gap，不选择替代机位。",
        "",
    ]
    for shot in plan["shots"]:
        if shot["camera_status"] != "NEED_NEW_CAMERA":
            continue
        req = shot["camera_requirement"]
        lines.extend([
            f"## {shot['shot_id']}",
            "",
            f"- Narrative Purpose: {shot['narrative_purpose']}",
            f"- Purpose: {req['purpose']}",
            f"- Scale: {req['scale']}",
            f"- Subject Zone: {req['subject_zone']}",
            f"- Axis Requirement: {req['axis_requirement']}",
            f"- Axis Status: {shot['axis_status']}",
            f"- Lens Intent: {req['lens_intent']}",
            f"- Composition Requirement: {shot['composition_intent']}",
            "",
        ])
    path = scene_dir / "CAMERA_REQUIREMENT.md"
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return path


def apply_director_plan(
    episode_id: str,
    episode_dir: Path,
    result_path: Path,
    *,
    allowed_actions: set[str] | None = None,
) -> tuple[str, list[str]]:
    state_root = episode_dir / "director_state"
    runtime_path = state_root / "Runtime_State.json"
    runtime = read_json(runtime_path)

    accepted_actions = allowed_actions or {"PLAN_CURRENT_SCENE"}
    if runtime["next_action"] not in accepted_actions:
        raise ValueError(
            f"当前 next_action={runtime['next_action']}，"
            "不能导入 Scene Director Plan。"
        )

    plan = read_json(result_path)
    current_scene = runtime["current_scene_id"]

    if plan["episode_id"] != episode_id:
        raise ValueError("Director Plan episode_id 与当前 Episode 不一致。")
    if plan["scene_id"] != current_scene:
        raise ValueError("Director Plan scene_id 与当前 Runtime Scene 不一致。")

    scene_dir = state_root / current_scene
    scene_state_path = scene_dir / "Scene_State.json"
    scene_state = read_json(scene_state_path)
    if plan["next_scene"] != scene_state["next_scene"]:
        raise ValueError(
            f"Director Plan next_scene={plan['next_scene']}，"
            f"但 Scene Skeleton 要求 {scene_state['next_scene']}。"
        )

    issues = validate_director_plan(plan)
    result = classify_issues(issues)
    stored_result = scene_dir / "Scene_Director_Plan_RESULT.json"
    if result_path.resolve() != stored_result.resolve():
        shutil.copy2(result_path, stored_result)

    if result != "PASS":
        write_json(
            scene_dir / "Director_Plan_Validation_Result.json",
            {
                "result": result,
                "issues": issues,
                "updated_at": utc_now(),
            },
        )
        if result == "NEED_NEW_CAMERA":
            scene_state["status"] = "CAMERA_REQUIRED"
            scene_state["updated_at"] = utc_now()
            write_json(scene_state_path, scene_state)
            sync_scene_index(episode_dir, scene_state)
            _write_camera_requirement(scene_dir, plan)
            runtime["scene_status"] = "CAMERA_REQUIRED"
            runtime["next_action"] = "NEED_NEW_CAMERA"
            runtime["pending_director_plan"] = stored_result.relative_to(
                episode_dir
            ).as_posix()
            runtime["pending_camera_match"] = None
            runtime["last_event"] = "DIRECTOR_PLAN_CAMERA_GAP"
        else:
            scene_state["plan_status"] = "DRAFT"
            scene_state["status"] = "PLANNING"
            scene_state["shot_count"] = 0
            scene_state["shots"] = []
            scene_state["updated_at"] = utc_now()
            write_json(scene_state_path, scene_state)
            sync_scene_index(episode_dir, scene_state)
            runtime["current_shot_id"] = ""
            runtime["scene_status"] = "PLANNING"
            runtime["next_action"] = "PLAN_CURRENT_SCENE"
            runtime["last_event"] = "DIRECTOR_PLAN_REPLAN_REQUIRED"
        runtime["updated_at"] = utc_now()
        validate_state_payload(runtime, "Runtime_State.schema.json")
        write_json(runtime_path, runtime)
        return result, issues

    compile_plan_to_state(plan, scene_dir)

    scene_state["plan_status"] = "QA_REQUIRED"
    scene_state["status"] = "DIRECTOR_QA"
    scene_state["shot_count"] = len(plan["shots"])
    scene_state["shots"] = [shot["shot_id"] for shot in plan["shots"]]
    scene_state["updated_at"] = utc_now()
    write_json(scene_state_path, scene_state)
    sync_scene_index(episode_dir, scene_state)

    runtime["scene_status"] = "DIRECTOR_QA"
    runtime["next_action"] = "DIRECTOR_QA_REQUIRED"
    runtime["pending_director_plan"] = stored_result.relative_to(
        episode_dir
    ).as_posix()
    runtime["last_event"] = "DIRECTOR_PLAN_IMPORTED_WAIT_QA"
    runtime["updated_at"] = utc_now()
    validate_state_payload(runtime, "Runtime_State.schema.json")
    write_json(runtime_path, runtime)

    write_json(
        scene_dir / "Director_Plan_Validation_Result.json",
        {
            "result": "PASS",
            "issues": [],
            "updated_at": utc_now(),
        },
    )
    return "PASS", []
