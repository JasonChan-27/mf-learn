from __future__ import annotations

from typing import Any


class PromptContractError(ValueError):
    pass


def _require_values(
    label: str,
    values: list[Any],
    prompt: str,
    issues: list[str],
) -> None:
    for value in values:
        if value not in (None, "") and str(value) not in prompt:
            issues.append(f"{label} 缺少 State 字段：{value}")


def validate_compiled_prompt_contract(
    shot: dict[str, Any],
    previous_frame: dict[str, Any],
    image_prompt: str,
    video_prompt: str,
) -> list[str]:
    """Check exact State-to-prompt transfer; never judge or redesign the Shot."""
    issues: list[str] = []

    if previous_frame.get("policy") != shot["continuity"]["previous_frame_policy"]:
        issues.append("Previous Frame Policy 与 Shot State 不一致")

    output = shot["output_format"]
    output_values = [
        f"Aspect Ratio: {output['aspect_ratio']}",
        f"Orientation: {output['orientation']}",
        f"Target Canvas: {output['width']}x{output['height']}",
    ]
    for label, prompt in (("IMAGE_PROMPT", image_prompt), ("VIDEO_PROMPT", video_prompt)):
        _require_values(label, output_values, prompt, issues)
        if "Do not output landscape" not in prompt:
            issues.append(f"{label} 缺少禁止横屏的技术锁")

    image_values: list[Any] = [
        shot["episode_id"],
        shot["scene_id"],
        shot["shot_id"],
        shot["primary_function"],
        shot["primary_focus"],
        shot["coverage"],
        shot["composition_intent"],
        shot["information_density"],
        shot["camera_state"]["camera_asset"],
        shot["camera_state"]["camera_status"],
        shot["camera_state"]["axis_status"],
        shot["continuity"]["mode"],
        previous_frame["policy"],
        previous_frame["instruction"],
        shot["start_state"]["description"],
        shot["frozen_moment"]["description"],
        *shot["visible_characters"],
        *shot["partial_characters"],
        *shot["off_screen_characters"],
        *shot["continuity"]["locked_facts"],
        *shot["continuity"]["change_allowed"],
        *shot["frozen_moment"]["physical_boundaries"],
        *shot["frozen_moment"]["forbidden_advanced_states"],
    ]
    _require_values("IMAGE_PROMPT", image_values, image_prompt, issues)

    video_values: list[Any] = [
        shot["episode_id"],
        shot["scene_id"],
        shot["shot_id"],
        shot["shot_delta"]["primary_action"],
        shot["shot_delta"]["performance_notes"],
        shot["camera_state"]["movement"],
        shot["camera_state"]["movement_reason"],
        shot["end_state"]["description"],
        shot["estimated_duration"],
        shot["continuity"]["mode"],
        *shot["shot_delta"]["secondary_actions"],
        *shot["shot_delta"]["timing"],
        *shot["continuity"]["locked_facts"],
        *shot["continuity"]["change_allowed"],
    ]
    _require_values("VIDEO_PROMPT", video_values, video_prompt, issues)

    forbidden_in_image: list[Any] = [
        shot["shot_delta"]["primary_action"],
        shot["shot_delta"]["performance_notes"],
        shot["camera_state"]["movement"],
        shot["camera_state"]["movement_reason"],
        shot["end_state"]["description"],
        *shot["shot_delta"]["secondary_actions"],
        *shot["shot_delta"]["timing"],
    ]
    for value in forbidden_in_image:
        if value not in (None, "") and str(value) in image_prompt:
            issues.append(f"IMAGE_PROMPT 泄漏 VIDEO-only State：{value}")

    return issues


# Compatibility alias for older callers.
validate_compiled_prompts = validate_compiled_prompt_contract
