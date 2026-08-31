from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any


COMPILER_MODE = "PURE_STATE_TRANSLATION"
LOCKED_PROMPT_FIELDS = [
    "episode_id",
    "scene_id",
    "shot_id",
    "primary_function",
    "primary_focus",
    "coverage",
    "composition_intent",
    "information_density",
    "output_format",
    "visible_characters",
    "partial_characters",
    "off_screen_characters",
    "camera_state",
    "continuity",
    "start_state",
    "frozen_moment",
    "shot_delta",
    "end_state",
    "estimated_duration",
]


def _lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None"


def _csv(items: list[str]) -> str:
    return ", ".join(items) if items else "None"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def prompt_source_state(
    shot: dict[str, Any],
    previous_frame: dict[str, Any],
) -> dict[str, Any]:
    """Return only immutable fields consumed by the pure compiler."""
    locked_state = {
        field: deepcopy(shot[field])
        for field in LOCKED_PROMPT_FIELDS
    }
    # Runtime records the resolved filename after compilation; it is not a
    # compiler input and must not invalidate the immutable source hash.
    locked_state["continuity"].pop("previous_frame_filename", None)
    return {
        "shot_state": locked_state,
        "previous_frame": {
            "policy": previous_frame["policy"],
            "instruction": previous_frame["instruction"],
            "include_previous_final_in_upload": previous_frame[
                "include_previous_final_in_upload"
            ],
            "previous_shot_id": previous_frame.get("previous_shot_id"),
        },
    }


def source_state_sha256(
    shot: dict[str, Any],
    previous_frame: dict[str, Any],
) -> str:
    canonical = json.dumps(
        prompt_source_state(shot, previous_frame),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return _sha256_text(canonical)


def compile_image_prompt(
    shot: dict[str, Any],
    previous_frame: dict[str, Any],
) -> str:
    """Translate locked Shot State into a still-image prompt without invention."""
    fm = shot["frozen_moment"]
    camera = shot["camera_state"]
    continuity = shot["continuity"]
    output = shot["output_format"]

    return f"""# IMAGE PROMPT

严格执行已经锁定的 Shot State；不得重新导演或补全缺失创意。

## Production Identity
- Episode: {shot['episode_id']}
- Scene: {shot['scene_id']}
- Shot: {shot['shot_id']}

## Output Format — Technical Lock
- Aspect Ratio: {output['aspect_ratio']}
- Orientation: {output['orientation']}
- Target Canvas: {output['width']}x{output['height']}

Generate a native vertical portrait composition on the locked canvas.
Do not output landscape. Do not letterbox or crop a landscape composition.
Recompose all reference assets naturally for the vertical frame; reference image
dimensions must never override this output format.
Camera Masters define camera position, direction, height and lens intent—not the
source canvas boundary. Environment Masters define spatial truth—not output ratio.

## Shot Execution
- Primary Function: {shot['primary_function']}
- Primary Focus: {shot['primary_focus']}
- Information Density: {shot['information_density']}

## Camera / Coverage
- Camera Asset: {camera['camera_asset']}
- Camera Status: {camera['camera_status']}
- Axis Status: {camera['axis_status']}
- Coverage: {shot['coverage']}
- Composition Intent: {shot['composition_intent']}

Camera Motion 只属于 VIDEO；静态 IMAGE 不得表现运镜后的结果。

## Character Visibility
- Visible: {_csv(shot['visible_characters'])}
- Partial: {_csv(shot['partial_characters'])}
- Off Screen: {_csv(shot['off_screen_characters'])}

不得把 Off Screen 角色重新加入画面。

## Continuity
- Mode: {continuity['mode']}
- Previous Frame Policy: {previous_frame['policy']}
- Previous Frame Instruction: {previous_frame['instruction']}
- Locked Facts: {_csv(continuity['locked_facts'])}
- Change Allowed: {_csv(continuity['change_allowed'])}

## Start State
{shot['start_state']['description']}

## Frozen Moment — IMAGE 最高动作状态真相
{fm['description']}

### Physical Boundaries
{_lines(fm['physical_boundaries'])}

### Forbidden Advanced States
{_lines(fm['forbidden_advanced_states'])}

## Still Image Contract
- IMAGE 必须停在 Frozen Moment。
- 不得执行 Shot Delta、End State 或下一 Shot 动作。
- 不得改变 Identity、Environment、Outfit、Props、Camera、Coverage 或 Composition Intent。
- 不得增加 Shot State 中不存在的角色、动作、道具或空间信息。
"""


def compile_video_prompt(shot: dict[str, Any]) -> str:
    """Translate locked temporal state into a motion-only prompt."""
    delta = shot["shot_delta"]
    camera = shot["camera_state"]
    continuity = shot["continuity"]
    output = shot["output_format"]

    return f"""# VIDEO PROMPT

严格从已批准的 IMAGE Frozen Moment 开始；不得重新导演。

## Production Identity
- Episode: {shot['episode_id']}
- Scene: {shot['scene_id']}
- Shot: {shot['shot_id']}

## Output Format — Technical Lock
- Aspect Ratio: {output['aspect_ratio']}
- Orientation: {output['orientation']}
- Target Canvas: {output['width']}x{output['height']}

The video must remain native vertical portrait throughout.
Do not output landscape, letterboxing or pillarboxing.

## Shot Delta
### Primary Action
{delta['primary_action']}

### Secondary Actions
{_lines(delta['secondary_actions'])}

### Performance Notes
{delta['performance_notes']}

### Timing
{_lines(delta['timing'])}

## Camera Motion
- Movement: {camera['movement']}
- Movement Reason: {camera['movement_reason']}

不得增加 Shot State 中不存在的额外运镜。

## End State
{shot['end_state']['description']}

## Duration
- Estimated Duration: {shot['estimated_duration']} seconds

## Continuity Lock
- Mode: {continuity['mode']}
- Locked Facts: {_csv(continuity['locked_facts'])}
- Change Allowed: {_csv(continuity['change_allowed'])}
- 只执行当前 Shot Delta，不得继续表演下一 Shot。
"""


def compile_handoff(
    shot: dict[str, Any],
    previous_frame: dict[str, Any],
) -> str:
    return f"""# ChatGPT Shot Handoff — {shot['scene_id']} {shot['shot_id']}

当前模式：SHOT_PROMPT_ONLY

请严格使用本目录中的：
- IMAGE_PROMPT.md
- VIDEO_PROMPT.md
- UPLOAD_MANIFEST.json
- PROMPT_COMPILATION_MANIFEST.json

规则：
- 只输出 Production Progress、IMAGE PROMPT、VIDEO PROMPT。
- 不调用图片生成。
- 不重新规划 Scene 或 Shot。
- 不改变 Camera / Coverage / Composition。
- 不把 VIDEO 动作提前到 IMAGE。
- 固定输出 {shot['output_format']['aspect_ratio']} / {shot['output_format']['orientation']} / {shot['output_format']['width']}x{shot['output_format']['height']}。
- Previous Frame Policy: {previous_frame['policy']}
- {previous_frame['instruction']}
"""


def compile_prompt_pair(
    shot: dict[str, Any],
    previous_frame: dict[str, Any],
) -> dict[str, str]:
    return {
        "image_prompt": compile_image_prompt(shot, previous_frame),
        "video_prompt": compile_video_prompt(shot),
        "handoff": compile_handoff(shot, previous_frame),
    }


def build_compilation_manifest(
    shot: dict[str, Any],
    previous_frame: dict[str, Any],
    prompts: dict[str, str],
) -> dict[str, Any]:
    return {
        "schema_version": "4.1",
        "episode_id": shot["episode_id"],
        "scene_id": shot["scene_id"],
        "shot_id": shot["shot_id"],
        "compiler_mode": COMPILER_MODE,
        "creative_decision_allowed": False,
        "output_format": deepcopy(shot["output_format"]),
        "source_state_sha256": source_state_sha256(shot, previous_frame),
        "image_prompt_sha256": _sha256_text(prompts["image_prompt"]),
        "video_prompt_sha256": _sha256_text(prompts["video_prompt"]),
        "handoff_sha256": _sha256_text(prompts["handoff"]),
        "locked_fields": LOCKED_PROMPT_FIELDS,
    }
