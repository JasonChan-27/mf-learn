from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from director_state import (
    read_json,
    sync_scene_index,
    utc_now,
    validate_state_payload,
    write_json,
)


ALLOWED_RESULTS = {"PASS", "REPLAN_REQUIRED", "NEED_NEW_CAMERA"}


def build_qa_request(
    episode_id: str,
    scene_dir: Path,
) -> Path:
    plan_path = scene_dir / "Scene_Director_Plan_RESULT.json"
    scene_plan_path = scene_dir / "Scene_Plan.json"
    if not plan_path.is_file() or not scene_plan_path.is_file():
        raise FileNotFoundError("Director Plan 尚未成功导入，不能执行 Director QA。")

    plan = read_json(plan_path)
    scene_plan = read_json(scene_plan_path)
    shot_summary = "\n".join(
        f"- {s['shot_id']}: {s['primary_function']} / {s['coverage']} / "
        f"{s['selected_camera'] or 'NO_CAMERA'} / {s['camera_motion']}"
        for s in scene_plan["shots"]
    )
    full_plan_json = json.dumps(plan, ensure_ascii=False, indent=2)

    text = f"""# {episode_id} {plan['scene_id']} — Director QA Request

你现在只执行 Director QA，不重新导演，不生成图片，不生成 IMAGE PROMPT / VIDEO PROMPT。

审核对象是已经完成 Planning Import 的完整 Scene。

## 当前 Shot Plan

{shot_summary}

## 完整 Scene Director Plan（审核唯一对象）

```json
{full_plan_json}
```

## 必须审核

1. Narrative Coverage
   - Scene Goal 是否被完整覆盖
   - 是否存在剧情信息缺失
   - Scene End 是否成立

2. Shot Necessity
   - 每个 Shot 是否真的必要
   - why_this_shot 是否成立
   - why_not_previous_shot 是否成立
   - 是否存在仅因微小动作变化而拆出的 Shot

3. Visual Differentiation
   - 相邻 Shot 的 Coverage / Camera / Composition / Information Density 是否有叙事理由
   - 是否出现连续多个视觉近似镜头
   - 是否缺少必要的 Reaction / Insert / Establishing / Transition

4. Camera & Motion
   - Camera 是否服务叙事
   - Camera Motion 是否必要
   - 不得为了“有运镜”而运镜
   - NEED_NEW_CAMERA 时必须明确指出

5. Continuity
   - SAME_CAMERA_CONTINUATION 是否真的需要继承上一 Final Frame
   - CAMERA_CUT_CONTINUITY 是否错误地把上一 Final Frame 当成最高优先级
   - 切镜时 Identity / Space / Lighting / Props / Action State 是否可连续

6. Frozen Moment
   - Image Prompt 首帧状态是否早于动作发生
   - physical_boundaries 是否可见、可验证
   - forbidden_advanced_states 是否阻止“准备起跳却已经跳起”等问题

7. Rhythm
   - Scene 是否被过度切碎
   - 是否景别单一
   - 是否缺少节奏变化
   - Shot Duration 是否大致合理

## 输出

只输出一个 JSON 对象，不要 Markdown 代码围栏：

{{
  "schema_version": "4.1",
  "episode_id": "{episode_id}",
  "scene_id": "{plan['scene_id']}",
  "result": "PASS | REPLAN_REQUIRED | NEED_NEW_CAMERA",
  "scene_score": 0,
  "dimension_scores": {{
    "narrative_coverage": 0,
    "shot_necessity": 0,
    "visual_differentiation": 0,
    "camera_and_motion": 0,
    "continuity": 0,
    "frozen_moment": 0,
    "rhythm": 0
  }},
  "issues": [
    {{
      "severity": "BLOCKER | MAJOR | MINOR",
      "shot_ids": ["ShotXX-XX"],
      "category": "string",
      "problem": "string",
      "required_change": "string"
    }}
  ],
  "approved_strengths": ["string"],
  "replan_instruction": "string or null"
}}

判定规则：

- PASS：没有 BLOCKER / MAJOR，且 scene_score >= 80。
- REPLAN_REQUIRED：存在导演结构问题；必须回到 Scene Planning，由 GPT Director 重规划。
- NEED_NEW_CAMERA：导演方案成立，但现有 Camera Library 无法执行关键镜头。
- 不允许在 QA JSON 中直接偷偷修改 Shot Plan。
"""
    path = scene_dir / "DIRECTOR_QA_REQUEST.md"
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def validate_qa_result(
    qa: dict[str, Any],
    episode_id: str,
    scene_id: str,
) -> list[str]:
    issues: list[str] = []
    try:
        validate_state_payload(qa, "Director_QA_Result.schema.json")
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        issues.append(str(exc))
        return issues
    required = [
        "schema_version", "episode_id", "scene_id", "result",
        "scene_score", "dimension_scores", "issues",
        "approved_strengths", "replan_instruction",
    ]
    for key in required:
        if key not in qa:
            issues.append(f"缺少字段：{key}")

    if issues:
        return issues

    if qa["episode_id"] != episode_id:
        issues.append("episode_id 不匹配")
    if qa["scene_id"] != scene_id:
        issues.append("scene_id 不匹配")
    if qa["result"] not in ALLOWED_RESULTS:
        issues.append(f"非法 result：{qa['result']}")

    score = qa["scene_score"]
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("scene_score 必须为 0~100")

    dims = qa["dimension_scores"]
    expected_dims = {
        "narrative_coverage", "shot_necessity",
        "visual_differentiation", "camera_and_motion",
        "continuity", "frozen_moment", "rhythm",
    }
    if set(dims) != expected_dims:
        issues.append("dimension_scores 字段不完整")
    else:
        for key, value in dims.items():
            if not isinstance(value, (int, float)) or not 0 <= value <= 100:
                issues.append(f"{key} 必须为 0~100")

    severities = []
    for idx, item in enumerate(qa["issues"]):
        for key in ["severity", "shot_ids", "category", "problem", "required_change"]:
            if key not in item:
                issues.append(f"issues[{idx}] 缺少 {key}")
        if "severity" in item:
            severities.append(item["severity"])
            if item["severity"] not in {"BLOCKER", "MAJOR", "MINOR"}:
                issues.append(f"issues[{idx}] severity 非法")

    if qa["result"] == "PASS":
        if score < 80:
            issues.append("PASS 时 scene_score 必须 >= 80")
        if any(s in {"BLOCKER", "MAJOR"} for s in severities):
            issues.append("存在 BLOCKER/MAJOR 时不能 PASS")
    elif qa["result"] == "REPLAN_REQUIRED":
        if not qa["replan_instruction"]:
            issues.append("REPLAN_REQUIRED 必须提供 replan_instruction")
    elif qa["result"] == "NEED_NEW_CAMERA":
        if not qa["replan_instruction"]:
            issues.append("NEED_NEW_CAMERA 必须说明 Camera Requirement")

    return issues


def apply_qa_result(
    episode_id: str,
    episode_dir: Path,
    result_path: Path,
) -> tuple[str, list[str]]:
    state_root = episode_dir / "director_state"
    runtime_path = state_root / "Runtime_State.json"
    runtime = read_json(runtime_path)
    if runtime["next_action"] != "DIRECTOR_QA_REQUIRED":
        raise ValueError(
            f"当前 next_action={runtime['next_action']}，不能导入 Director QA。"
        )

    scene_id = runtime["current_scene_id"]
    scene_dir = state_root / scene_id
    qa = read_json(result_path)
    validation = validate_qa_result(qa, episode_id, scene_id)
    if validation:
        return "INVALID_QA_RESULT", validation

    stored = scene_dir / "Director_QA_RESULT.json"
    if result_path.resolve() != stored.resolve():
        stored.write_text(
            json.dumps(qa, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    scene_state_path = scene_dir / "Scene_State.json"
    scene_state = read_json(scene_state_path)

    if qa["result"] == "PASS":
        scene_plan_path = scene_dir / "Scene_Plan.json"
        scene_plan = read_json(scene_plan_path)
        scene_plan["plan_status"] = "LOCKED"
        scene_plan["director_qa"] = {
            "result": "PASS",
            "scene_score": qa["scene_score"],
            "dimension_scores": qa["dimension_scores"],
        }
        validate_state_payload(scene_plan, "Scene_Plan.schema.json")
        write_json(scene_plan_path, scene_plan)

        scene_state["plan_status"] = "LOCKED"
        scene_state["status"] = "PRODUCTION"
        scene_state["updated_at"] = utc_now()
        write_json(scene_state_path, scene_state)
        sync_scene_index(episode_dir, scene_state)

        first_shot = scene_state["shots"][0]
        first_shot_path = scene_dir / "shots" / f"{first_shot}_State.json"
        first_state = read_json(first_shot_path)
        first_state["status"] = "READY"
        validate_state_payload(first_state, "Shot_State.schema.json")
        write_json(first_shot_path, first_state)

        runtime["current_shot_id"] = first_shot
        runtime["scene_status"] = "PRODUCTION"
        runtime["next_action"] = "GENERATE_CURRENT_SHOT_PACKAGE"
        runtime["pending_director_qa"] = stored.relative_to(
            episode_dir
        ).as_posix()
        runtime["last_event"] = "DIRECTOR_QA_PASS_SCENE_LOCKED"
        runtime["updated_at"] = utc_now()
        validate_state_payload(runtime, "Runtime_State.schema.json")
        write_json(runtime_path, runtime)
        return "PASS", []

    if qa["result"] == "NEED_NEW_CAMERA":
        scene_state["plan_status"] = "QA_REQUIRED"
        scene_state["status"] = "CAMERA_REQUIRED"
        scene_state["updated_at"] = utc_now()
        write_json(scene_state_path, scene_state)
        sync_scene_index(episode_dir, scene_state)

        runtime["scene_status"] = "CAMERA_REQUIRED"
        runtime["next_action"] = "NEED_NEW_CAMERA"
        runtime["pending_director_qa"] = stored.relative_to(
            episode_dir
        ).as_posix()
        runtime["last_event"] = "DIRECTOR_QA_CAMERA_REQUIRED"
        runtime["updated_at"] = utc_now()
        issue_lines = []
        for issue in qa["issues"]:
            issue_lines.append(
                f"- {', '.join(issue['shot_ids']) or 'Scene'}: "
                f"{issue['problem']} → {issue['required_change']}"
            )
        requirement = scene_dir / "CAMERA_REQUIREMENT.md"
        requirement.write_text(
            "# Camera Requirement\n\n"
            f"- Episode: {episode_id}\n"
            f"- Scene: {scene_id}\n\n"
            "Python 不选择替代机位；以下内容原样来自 Director QA。\n\n"
            "## QA Requirement\n\n"
            f"{qa['replan_instruction']}\n\n"
            "## Issues\n\n"
            + ("\n".join(issue_lines) if issue_lines else "- No structured issue supplied")
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        validate_state_payload(runtime, "Runtime_State.schema.json")
        write_json(runtime_path, runtime)
        return "NEED_NEW_CAMERA", []

    # REPLAN_REQUIRED
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
    runtime["pending_director_qa"] = stored.relative_to(
        episode_dir
    ).as_posix()
    runtime["last_event"] = "DIRECTOR_QA_REPLAN_REQUIRED"
    runtime["updated_at"] = utc_now()
    validate_state_payload(runtime, "Runtime_State.schema.json")
    write_json(runtime_path, runtime)
    return "REPLAN_REQUIRED", []
