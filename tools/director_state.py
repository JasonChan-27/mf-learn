from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT
from schema_validator import assert_valid


STATE_SCHEMA_VERSION = "4.1"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_state_payload(payload: dict[str, Any], schema_name: str) -> None:
    schema_path = PROJECT_ROOT / "director" / "STATE" / schema_name
    if not schema_path.is_file():
        raise FileNotFoundError(f"State Schema 不存在：{schema_path}")
    schema = read_json(schema_path)
    assert_valid(payload, schema, schema_name)


def normalize_scene_id(value: str | int) -> str:
    if isinstance(value, int):
        return f"Scene{value:02d}"
    match = re.search(r"(\d+)", str(value))
    if not match:
        raise ValueError(f"无法识别 Scene ID: {value}")
    return f"Scene{int(match.group(1)):02d}"


def parse_scene_manifest(confirmed_script: Path) -> list[dict[str, Any]]:
    text = confirmed_script.read_text(encoding="utf-8-sig")
    patterns = [
        re.compile(r"^#{1,6}\s*Scene\s*0*(\d+)(?:\s*[-—:：|｜]?\s*(.*))?$", re.I),
        re.compile(r"^#{1,6}\s*场景\s*0*(\d+)(?:\s*[-—:：|｜]?\s*(.*))?$"),
    ]

    result: list[dict[str, Any]] = []
    seen: set[int] = set()

    for raw in text.splitlines():
        line = raw.strip()
        for pattern in patterns:
            match = pattern.match(line)
            if not match:
                continue
            number = int(match.group(1))
            if number in seen:
                break
            seen.add(number)
            result.append(
                {
                    "scene_id": f"Scene{number:02d}",
                    "scene_number": number,
                    "title": (match.group(2) or "").strip(),
                }
            )
            break

    if not result:
        raise ValueError(
            f"Confirmed Script 中没有识别到 Scene 标题：{confirmed_script}"
        )
    return result


def create_scene_skeleton(
    episode_id: str,
    scene: dict[str, Any],
    next_scene: str,
) -> dict[str, Any]:
    return {
        "schema_version": STATE_SCHEMA_VERSION,
        "episode_id": episode_id,
        "scene_id": scene["scene_id"],
        "scene_number": scene["scene_number"],
        "scene_title": scene.get("title", ""),
        "plan_status": "DRAFT",
        "status": "PLANNING",
        "shot_count": 0,
        "shots": [],
        "next_scene": next_scene,
        "updated_at": utc_now(),
    }


def create_runtime_state(
    episode_id: str,
    first_scene_id: str,
) -> dict[str, Any]:
    return {
        "schema_version": STATE_SCHEMA_VERSION,
        "episode_id": episode_id,
        "current_scene_id": first_scene_id,
        "current_shot_id": "",
        "director_session_mode": "PROMPT_ONLY",
        "scene_status": "PLANNING",
        "next_action": "PLAN_CURRENT_SCENE",
        "pending_director_plan": None,
        "pending_director_qa": None,
        "pending_camera_match": None,
        "last_event": "EPISODE_INITIALIZED_WAIT_DIRECTOR",
        "updated_at": utc_now(),
    }


def director_state_root(episode_dir: Path) -> Path:
    return episode_dir / "director_state"


def sync_scene_index(episode_dir: Path, scene_state: dict[str, Any]) -> None:
    """Keep the navigation index aligned with the authoritative Scene State."""
    index_path = director_state_root(episode_dir) / "Director_State_Index.json"
    if not index_path.is_file():
        return
    index = read_json(index_path)
    for item in index.get("scenes", []):
        if item.get("scene_id") != scene_state.get("scene_id"):
            continue
        item["plan_status"] = scene_state["plan_status"]
        item["status"] = scene_state["status"]
        item["shot_count"] = scene_state["shot_count"]
        break
    index["updated_at"] = utc_now()
    write_json(index_path, index)


def initialize_director_state(
    episode_id: str,
    episode_dir: Path,
    *,
    reset: bool = False,
) -> Path:
    """
    V4.1 Phase2-B:
    - 只建立 Runtime + Scene Skeleton。
    - 所有 Scene（包括 Scene01）全部进入 PLANNING。
    - 不创建任何 Shot State。
    - 不读取任何 Scene Plan example / fixture。
    """
    state_root = director_state_root(episode_dir)

    if reset and state_root.exists():
        shutil.rmtree(state_root)

    if state_root.exists() and (state_root / "Runtime_State.json").is_file():
        return state_root

    confirmed_script = episode_dir / "Confirmed_Script.md"
    scenes = parse_scene_manifest(confirmed_script)
    state_root.mkdir(parents=True, exist_ok=True)

    index_scenes: list[dict[str, Any]] = []

    for idx, scene in enumerate(scenes):
        next_scene = (
            scenes[idx + 1]["scene_id"]
            if idx + 1 < len(scenes)
            else "EPISODE_END"
        )
        scene_dir = state_root / scene["scene_id"]
        scene_dir.mkdir(parents=True, exist_ok=True)

        skeleton = create_scene_skeleton(
            episode_id,
            scene,
            next_scene,
        )
        write_json(scene_dir / "Scene_State.json", skeleton)

        index_scenes.append(
            {
                "scene_id": scene["scene_id"],
                "scene_number": scene["scene_number"],
                "scene_title": scene.get("title", ""),
                "plan_status": "DRAFT",
                "status": "PLANNING",
                "shot_count": 0,
                "path": f"{scene['scene_id']}/Scene_State.json",
            }
        )

    runtime = create_runtime_state(
        episode_id,
        scenes[0]["scene_id"],
    )
    validate_state_payload(runtime, "Runtime_State.schema.json")
    write_json(state_root / "Runtime_State.json", runtime)

    write_json(
        state_root / "Director_State_Index.json",
        {
            "schema_version": STATE_SCHEMA_VERSION,
            "episode_id": episode_id,
            "scene_count": len(scenes),
            "scenes": index_scenes,
            "runtime_state": "Runtime_State.json",
            "updated_at": utc_now(),
        },
    )
    return state_root


def scene_plan_template(
    episode_id: str,
    scene_state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "4.1",
        "episode_id": episode_id,
        "scene_id": scene_state["scene_id"],
        "revision": 1,
        "plan_status": "LOCKED",
        "scene_director_decision": {
            "scene_goal": "",
            "narrative_change": "",
            "primary_character": "",
            "secondary_characters": [],
            "audience_start_state": "",
            "audience_end_state": "",
            "emotion_curve": [],
            "information_curve": [],
            "rhythm_strategy": "",
            "primary_style": "",
            "secondary_style": None,
            "scene_visual_strategy": "",
            "scene_camera_strategy": "",
            "scene_end_intent": "",
        },
        "scene_assets": {
            "environment_asset": "",
            "character_assets": {},
            "outfit_assets": {},
            "prop_assets": [],
        },
        "shots": [],
        "scene_end_state": {
            "description": "",
        },
        "next_scene": scene_state.get("next_scene", "EPISODE_END"),
    }


def planning_request_text(
    episode_id: str,
    scene_state: dict[str, Any],
) -> str:
    scene_id = scene_state["scene_id"]
    title = scene_state.get("scene_title", "")
    return f"""# {episode_id} {scene_id} — Scene Director Planning Request

当前为 V4.1 Director Planning 阶段。

当前 Scene：
- Scene：{scene_id}
- 标题：{title or "以 Confirmed Script 为准"}
- 当前状态：PLANNING
- 当前 Shot 数：0

请严格读取 Production Context Package 中的：

- Confirmed Script
- Creative Brief
- Bible
- Asset Registry / Asset Selection
- Director Guidelines
- V4.1 Architecture Specification
- Scene_Director_Plan.schema.json
- Director_Decision.schema.json
- Camera / Coverage / Continuity 规则（如包内存在）

在内部完成：

1. Scene Director Decision
2. Shot Candidate Planning
3. Director Style Ranking
4. Shot Planning
5. Coverage Planning
6. Camera Planning
7. Planning QA

必须输出一个完整、可直接保存的 JSON 对象。

JSON 必须符合：
director/STATE/Scene_Director_Plan.schema.json

硬性要求：

- 只输出 JSON，不输出 Markdown 代码围栏。
- 不输出 IMAGE PROMPT / VIDEO PROMPT。
- 不输出内部推理。
- Shot 数量由 GPT Director 根据剧情与节奏自主决定，Python 不预设。
- 每个 Shot 必须填写 why_this_shot。
- 每个 Shot 必须填写 why_not_previous_shot。
- 每个 Shot 必须填写 composition_intent。
- Camera / Coverage / Camera Motion / Axis Status 必须由导演决定并说明理由。
- 每个 Shot 必须填写 coverage_reason；Python 不根据 composition_intent 反推理由。
- scene_assets.character_assets 必须由 GPT Director 显式映射角色名到 Character Master ID。
- 每个 visible / partial character 都必须有映射；Python 不会按角色名猜资产。
- frozen_moment.physical_boundaries 必须是可见、可验证的物理边界。
- frozen_moment.forbidden_advanced_states 必须明确禁止首帧提前发生的状态。
- 微小动作变化不得单独拆成新 Shot。
- 最后一镜 scene_end 必须为 true。
- 最后一镜 next_shot 必须明确指向下一 Scene 或 EPISODE_END。
"""


def ensure_scene_planning_files(
    episode_id: str,
    episode_dir: Path,
) -> tuple[Path, Path]:
    state_root = director_state_root(episode_dir)
    runtime = read_json(state_root / "Runtime_State.json")

    if runtime.get("next_action") != "PLAN_CURRENT_SCENE":
        raise ValueError(
            "当前 Runtime 不处于 PLAN_CURRENT_SCENE，不能生成 Scene Planning 请求。"
        )

    scene_id = normalize_scene_id(runtime["current_scene_id"])
    scene_dir = state_root / scene_id
    scene_state = read_json(scene_dir / "Scene_State.json")

    request_path = scene_dir / "SCENE_PLANNING_REQUEST.md"
    template_path = scene_dir / "Scene_Director_Plan_TEMPLATE.json"

    request_path.write_text(
        planning_request_text(episode_id, scene_state),
        encoding="utf-8",
        newline="\n",
    )
    write_json(
        template_path,
        scene_plan_template(episode_id, scene_state),
    )
    return request_path, template_path
