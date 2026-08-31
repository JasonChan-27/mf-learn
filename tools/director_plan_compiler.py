from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from director_state import validate_state_payload, write_json
from production_format import locked_output_format


def compile_director_decision(
    plan: dict[str, Any],
    shot: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "4.1",
        "episode_id": plan["episode_id"],
        "scene_id": plan["scene_id"],
        "shot_id": shot["shot_id"],
        "primary_function": shot["primary_function"],
        "secondary_effect": shot["secondary_effect"],
        "narrative_purpose": shot["narrative_purpose"],
        "audience_feeling": shot["audience_feeling"],
        "information_gain": shot["information_gain"],
        "why_this_shot": shot["why_this_shot"],
        "why_not_previous_shot": shot["why_not_previous_shot"],
        "coverage_reason": shot["coverage_reason"],
        "camera_reason": shot["camera_reason"],
        "camera_motion_reason": shot["camera_motion_reason"],
        "continuity_reason": (
            f"{shot['continuity_mode']} / {shot['previous_frame_policy']}"
        ),
        "freeze_reason": shot["frozen_moment"]["description"],
    }


def compile_scene_plan(plan: dict[str, Any]) -> dict[str, Any]:
    assets = plan["scene_assets"]
    return {
        "schema_version": "4.1",
        "episode_id": plan["episode_id"],
        "scene_id": plan["scene_id"],
        "director_plan_revision": plan["revision"],
        "plan_status": "QA_REQUIRED",
        "scene_goal": plan["scene_director_decision"]["scene_goal"],
        "environment_asset": assets["environment_asset"],
        "character_assets": assets["character_assets"],
        "outfit_assets": assets["outfit_assets"],
        "prop_assets": assets["prop_assets"],
        "shot_count": len(plan["shots"]),
        "shots": [
            {
                "shot_id": shot["shot_id"],
                "order": shot["order"],
                "primary_function": shot["primary_function"],
                "primary_focus": shot["primary_focus"],
                "coverage": shot["coverage"],
                "composition_intent": shot["composition_intent"],
                "selected_camera": shot["selected_camera"],
                "camera_status": shot["camera_status"],
                "camera_motion": shot["camera_motion"],
                "continuity_mode": shot["continuity_mode"],
                "previous_frame_policy": shot["previous_frame_policy"],
                "visible_characters": shot["visible_characters"],
                "partial_characters": shot["partial_characters"],
                "off_screen_characters": shot["off_screen_characters"],
                "estimated_duration": shot["estimated_duration"],
                "scene_end": shot["scene_end"],
                "next_shot": shot["next_shot"],
            }
            for shot in plan["shots"]
        ],
        "scene_end_state": plan["scene_end_state"],
        "next_scene": plan["next_scene"],
    }


def compile_shot_state(
    plan: dict[str, Any],
    shot: dict[str, Any],
) -> dict[str, Any]:
    scene_assets = plan["scene_assets"]
    relevant_characters = list(dict.fromkeys(
        shot["visible_characters"] + shot["partial_characters"]
    ))
    asset_ids = []
    if scene_assets["environment_asset"]:
        asset_ids.append(scene_assets["environment_asset"])
    asset_ids.extend(
        scene_assets["character_assets"][character]
        for character in relevant_characters
        if character in scene_assets["character_assets"]
    )
    asset_ids.extend(
        scene_assets["outfit_assets"][character]
        for character in relevant_characters
        if character in scene_assets["outfit_assets"]
    )
    asset_ids.extend(scene_assets["prop_assets"])
    if shot["selected_camera"]:
        asset_ids.append(shot["selected_camera"])

    # Consume only the Director's explicit asset mappings. Never infer a
    # character, outfit, prop, or camera asset from role names in Python.
    return {
        "schema_version": "4.1",
        "episode_id": plan["episode_id"],
        "scene_id": plan["scene_id"],
        "shot_id": shot["shot_id"],
        "order": shot["order"],
        "status": "PLANNED",
        "primary_function": shot["primary_function"],
        "primary_focus": shot["primary_focus"],
        "coverage": shot["coverage"],
        "composition_intent": shot["composition_intent"],
        "information_density": shot["information_density"],
        "output_format": locked_output_format(),
        "visible_characters": shot["visible_characters"],
        "partial_characters": shot["partial_characters"],
        "off_screen_characters": shot["off_screen_characters"],
        "camera_state": {
            "camera_asset": shot["selected_camera"],
            "camera_status": shot["camera_status"],
            "movement": shot["camera_motion"],
            "movement_reason": shot["camera_motion_reason"],
            "axis_status": shot["axis_status"],
        },
        "continuity": {
            "mode": shot["continuity_mode"],
            "previous_frame_policy": shot["previous_frame_policy"],
            "previous_frame_filename": None,
            "locked_facts": [
                "Identity",
                "Space",
                "Lighting",
                "Props",
                "Action State",
            ],
            "change_allowed": (
                []
                if shot["continuity_mode"] == "SAME_CAMERA_CONTINUATION"
                else ["Coverage", "Camera", "Composition"]
            ),
        },
        "start_state": shot["start_state"],
        "frozen_moment": shot["frozen_moment"],
        "shot_delta": shot["shot_delta"],
        "end_state": {
            **shot["end_state"],
            "next_state_anchor": (
                shot["next_shot"]
                if shot["next_shot"]
                else plan["next_scene"]
            ),
        },
        "required_assets": {
            "asset_ids": list(dict.fromkeys(asset_ids)),
            "package_filenames": [],
        },
        "estimated_duration": shot["estimated_duration"],
        "scene_end": shot["scene_end"],
        "next_shot": shot["next_shot"],
    }


def compile_plan_to_state(
    plan: dict[str, Any],
    scene_dir: Path,
) -> None:
    decisions_dir = scene_dir / "decisions"
    shots_dir = scene_dir / "shots"
    if decisions_dir.exists():
        shutil.rmtree(decisions_dir)
    if shots_dir.exists():
        shutil.rmtree(shots_dir)
    decisions_dir.mkdir(parents=True, exist_ok=True)
    shots_dir.mkdir(parents=True, exist_ok=True)

    scene_plan = compile_scene_plan(plan)
    validate_state_payload(scene_plan, "Scene_Plan.schema.json")
    write_json(scene_dir / "Scene_Plan.json", scene_plan)

    for shot in plan["shots"]:
        decision = compile_director_decision(plan, shot)
        shot_state = compile_shot_state(plan, shot)
        validate_state_payload(decision, "Director_Decision.schema.json")
        validate_state_payload(shot_state, "Shot_State.schema.json")
        write_json(
            decisions_dir / f"{shot['shot_id']}_DirectorDecision.json",
            decision,
        )
        write_json(
            shots_dir / f"{shot['shot_id']}_State.json",
            shot_state,
        )
