from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from build_shot_package import AssetRequirementError, build_current_shot_package
from common import PROJECT_ROOT
from director_state import (
    read_json,
    sync_scene_index,
    utc_now,
    validate_state_payload,
    write_json,
)
from image_metadata import require_portrait_image
from production_format import ensure_shot_output_format


def _state_paths(episode_dir: Path, runtime: dict[str, Any]):
    scene_id = runtime["current_scene_id"]
    shot_id = runtime["current_shot_id"]
    scene_dir = episode_dir / "director_state" / scene_id
    shot_state_path = scene_dir / "shots" / f"{shot_id}_State.json"
    return scene_dir, shot_state_path


def approve_image(
    episode_id: str,
    episode_dir: Path,
    final_image: Path,
) -> str:
    runtime_path=episode_dir/"director_state"/"Runtime_State.json"
    runtime=read_json(runtime_path)
    if runtime["next_action"]!="WAIT_FOR_IMAGE_APPROVAL":
        raise ValueError(f"当前 next_action={runtime['next_action']}，不能批准图片。")
    scene_dir, shot_path=_state_paths(episode_dir,runtime)
    shot=read_json(shot_path)
    ensure_shot_output_format(shot)

    if not final_image.is_file():
        raise FileNotFoundError(f"Final 图片不存在：{final_image}")
    ext=final_image.suffix.lower()
    if ext not in {".png",".jpg",".jpeg",".webp"}:
        raise ValueError("Final 图片必须为 png/jpg/jpeg/webp。")
    require_portrait_image(final_image, "Final 图片")

    package_dir=episode_dir/"production"/runtime["current_scene_id"]/runtime["current_shot_id"]
    package_dir.mkdir(parents=True,exist_ok=True)
    final_dest=package_dir/f"{runtime['current_shot_id']}_Final{ext}"
    if final_image.resolve()!=final_dest.resolve():
        shutil.copy2(final_image,final_dest)

    shot["status"]="IMAGE_APPROVED"
    shot["approved_image"]=str(final_dest.relative_to(PROJECT_ROOT))
    validate_state_payload(shot, "Shot_State.schema.json")
    write_json(shot_path,shot)

    runtime["next_action"]="WAIT_FOR_VIDEO_APPROVAL"
    runtime["last_event"]="CURRENT_SHOT_IMAGE_APPROVED"
    runtime["updated_at"]=utc_now()
    validate_state_payload(runtime, "Runtime_State.schema.json")
    write_json(runtime_path,runtime)
    return str(final_dest)


def approve_video(
    episode_id: str,
    episode_dir: Path,
    video_file: Path | None = None,
) -> str:
    runtime_path=episode_dir/"director_state"/"Runtime_State.json"
    runtime=read_json(runtime_path)
    if runtime["next_action"]!="WAIT_FOR_VIDEO_APPROVAL":
        raise ValueError(f"当前 next_action={runtime['next_action']}，不能批准视频。")
    scene_dir, shot_path=_state_paths(episode_dir,runtime)
    shot=read_json(shot_path)
    ensure_shot_output_format(shot)

    if video_file is not None:
        if not video_file.is_file():
            raise FileNotFoundError(f"视频不存在：{video_file}")
        package_dir=episode_dir/"production"/runtime["current_scene_id"]/runtime["current_shot_id"]
        dest=package_dir/f"{runtime['current_shot_id']}_Video{video_file.suffix.lower()}"
        if video_file.resolve()!=dest.resolve():
            shutil.copy2(video_file,dest)
        shot["approved_video"]=str(dest.relative_to(PROJECT_ROOT))

    shot["status"]="COMPLETED"
    validate_state_payload(shot, "Shot_State.schema.json")
    write_json(shot_path,shot)
    return advance_after_shot(episode_id,episode_dir)


def advance_after_shot(episode_id: str, episode_dir: Path) -> str:
    runtime_path=episode_dir/"director_state"/"Runtime_State.json"
    runtime=read_json(runtime_path)
    scene_id=runtime["current_scene_id"]
    scene_dir=episode_dir/"director_state"/scene_id
    shot_path=scene_dir/"shots"/f"{runtime['current_shot_id']}_State.json"
    shot=read_json(shot_path)
    ensure_shot_output_format(shot)

    if not shot["scene_end"]:
        next_id=shot["next_shot"]
        next_path=scene_dir/"shots"/f"{next_id}_State.json"
        nxt=read_json(next_path)
        ensure_shot_output_format(nxt)
        nxt["status"]="READY"
        validate_state_payload(nxt, "Shot_State.schema.json")
        write_json(next_path,nxt)
        runtime["current_shot_id"]=next_id
        runtime["next_action"]="GENERATE_CURRENT_SHOT_PACKAGE"
        runtime["last_event"]="ADVANCED_TO_NEXT_SHOT"
        runtime["updated_at"]=utc_now()
        validate_state_payload(runtime, "Runtime_State.schema.json")
        write_json(runtime_path,runtime)
        return f"NEXT_SHOT:{next_id}"

    scene_state_path=scene_dir/"Scene_State.json"
    scene_state=read_json(scene_state_path)
    scene_state["status"]="COMPLETED"
    scene_state["updated_at"]=utc_now()
    write_json(scene_state_path,scene_state)
    sync_scene_index(episode_dir, scene_state)

    next_scene=scene_state["next_scene"]
    runtime["pending_director_plan"]=None
    runtime["pending_director_qa"]=None
    runtime["pending_camera_match"]=None
    if next_scene=="EPISODE_END":
        runtime["scene_status"]="COMPLETED"
        runtime["current_shot_id"]=""
        runtime["next_action"]="EPISODE_COMPLETE"
        runtime["last_event"]="EPISODE_COMPLETED"
    else:
        next_scene_state_path=(
            episode_dir/"director_state"/next_scene/"Scene_State.json"
        )
        next_scene_state=read_json(next_scene_state_path)
        next_scene_state["updated_at"]=utc_now()
        write_json(next_scene_state_path,next_scene_state)
        sync_scene_index(episode_dir,next_scene_state)
        runtime["current_scene_id"]=next_scene
        runtime["current_shot_id"]=""
        runtime["scene_status"]="PLANNING"
        runtime["next_action"]="PLAN_CURRENT_SCENE"
        runtime["last_event"]="SCENE_COMPLETED_ADVANCE_TO_PLANNING"
    runtime["updated_at"]=utc_now()
    validate_state_payload(runtime, "Runtime_State.schema.json")
    write_json(runtime_path,runtime)
    return f"SCENE_END:{next_scene}"
