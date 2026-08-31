from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from build_shot_package import (
    AssetRequirementError,
    build_current_shot_package,
    refresh_stale_current_package_state,
)
from camera_match import apply_camera_match, resume_camera_gap_after_build
from common import PROJECT_ROOT, normalize_episode_id
from director_plan_importer import apply_director_plan
from director_qa import build_qa_request, apply_qa_result
from production_runtime import (
    approve_image,
    approve_video,
)
from director_state import (
    director_state_root,
    ensure_scene_planning_files,
    read_json,
)


def invoke_build(episode_id: str, *, reset: bool) -> None:
    command = [
        sys.executable,
        str(PROJECT_ROOT / "tools" / "build_episode.py"),
        episode_id,
    ]
    if reset:
        command.append("--reset-director-state")

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError("build_episode.py 执行失败。")


def load_runtime(episode_id: str) -> dict:
    episode_dir = PROJECT_ROOT / "episodes" / episode_id
    path = director_state_root(episode_dir) / "Runtime_State.json"
    if not path.is_file():
        raise FileNotFoundError(
            "Director State 尚未初始化，请执行 --reset。"
        )
    return read_json(path)


def print_runtime(runtime: dict) -> None:
    print(json.dumps(runtime, ensure_ascii=False, indent=2))


def print_reference_warnings(package_dir: Path) -> None:
    manifest_path = package_dir / "PACKAGE_MANIFEST.json"
    if not manifest_path.is_file():
        return
    warnings = read_json(manifest_path).get("reference_warnings", [])
    if not warnings:
        return
    print("\nReference Format Suggestions（不阻塞生产）")
    for warning in warnings:
        print(
            f"- {warning.get('asset_id')} — {warning.get('reason')}: "
            f"{warning.get('details', '')}"
        )


def handle_current_action(episode_id: str) -> None:
    episode_dir = PROJECT_ROOT / "episodes" / episode_id
    runtime = load_runtime(episode_id)
    action = runtime.get("next_action")

    print("\nDirector Runtime")
    print_runtime(runtime)

    if action == "PLAN_CURRENT_SCENE":
        request_path, template_path = ensure_scene_planning_files(
            episode_id,
            episode_dir,
        )
        scene_id = runtime["current_scene_id"]

        print("\nNext: GPT Director Planning")
        print(f"Current Scene: {scene_id}")
        print("Shot Count: 0（尚未由导演决定）")
        print("\nGenerated:")
        print(request_path.relative_to(PROJECT_ROOT))
        print(template_path.relative_to(PROJECT_ROOT))
        print("\n操作：")
        print("1. 新建/进入导演规划对话。")
        print("2. 上传最新 Production Package。")
        print(
            "3. 发送 "
            f"{request_path.relative_to(PROJECT_ROOT)} 的完整内容。"
        )
        print("4. 将 GPT 返回的纯 JSON 保存为 Scene_Director_Plan_RESULT.json。")
        print(
            "5. 执行：python3.12 tools/run.py "
            f"{episode_id} --apply-director-plan <Scene_Director_Plan_RESULT.json>"
        )
        return

    if action == "DIRECTOR_QA_REQUIRED":
        scene_id = runtime["current_scene_id"]
        qa_path = build_qa_request(
            episode_id,
            episode_dir / "director_state" / scene_id,
        )
        print("\nNext: GPT Director QA")
        print(f"Generated: {qa_path.relative_to(PROJECT_ROOT)}")
        print("请上传最新 Production Package，并将该文件完整发送给 Director QA 对话。")
        print("将返回的纯 JSON 保存为 Director_QA_RESULT.json，然后执行：")
        print(
            "python3.12 tools/run.py "
            f"{episode_id} --apply-director-qa <Director_QA_RESULT.json>"
        )
        return

    if action == "CAMERA_MATCH_REQUIRED":
        scene_id = runtime["current_scene_id"]
        scene_dir = episode_dir / "director_state" / scene_id
        request_path = scene_dir / "CAMERA_MATCH_REQUEST.md"
        template_path = scene_dir / "Camera_Match_Result_TEMPLATE.json"
        print("\nNext: GPT Director Camera Match Resume")
        print("本步骤只补 Camera 映射，不重新规划 Scene 或改写其他 Shot 字段。")
        print(f"Request: {request_path.relative_to(PROJECT_ROOT)}")
        print(f"Template: {template_path.relative_to(PROJECT_ROOT)}")
        print("请上传最新 Production Package，并将 CAMERA_MATCH_REQUEST.md 完整发送给 GPT Director。")
        print("将返回的纯 JSON 保存为 Camera_Match_Result.json，然后执行：")
        print(
            "python3.12 tools/run.py "
            f"{episode_id} --apply-camera-match <Camera_Match_Result.json>"
        )
        return

    if action == "GENERATE_CURRENT_SHOT_PACKAGE":
        try:
            package_dir = build_current_shot_package(episode_id, episode_dir)
        except AssetRequirementError as exc:
            runtime = load_runtime(episode_id)
            scene_id = runtime["current_scene_id"]
            path = episode_dir / "director_state" / scene_id / "ASSET_REQUIREMENT.md"
            print("\n当前 Shot 缺少必需 Master 资产，生产已暂停。")
            print(exc)
            if path.is_file():
                print(f"Requirement: {path.relative_to(PROJECT_ROOT)}")
            return
        print("\nShot Package Generated")
        print(package_dir.relative_to(PROJECT_ROOT))
        print("请按 UPLOAD_MANIFEST.json 上传参考图。")
        print("按 UPLOAD_MANIFEST.json 与已编译的 IMAGE_PROMPT.md / VIDEO_PROMPT.md 执行生成。")
        print("不得让 GPT 重新导演或改写已编译 Prompt。")
        print_reference_warnings(package_dir)
        return

    if action == "WAIT_FOR_IMAGE_APPROVAL":
        print("\n等待当前 Shot 图片审核/批准。")
        print(
            "批准后执行：python3.12 tools/run.py "
            f"{episode_id} --approve-image <final-image-path>"
        )
        return

    if action == "WAIT_FOR_VIDEO_APPROVAL":
        print("\n当前图片已批准，等待视频完成。")
        print(
            "视频完成后执行：python3.12 tools/run.py "
            f"{episode_id} --approve-video <video-path>"
        )
        print("若暂时不保存视频文件，可使用 --approve-video-only。")
        return

    if action == "NEED_NEW_CAMERA":
        scene_id = runtime["current_scene_id"]
        path = episode_dir / "director_state" / scene_id / "CAMERA_REQUIREMENT.md"
        print("\n当前 Scene 缺少可执行 Camera Master，生产已暂停。")
        if path.is_file():
            print(f"Requirement: {path.relative_to(PROJECT_ROOT)}")
        print(
            "创建并登记 Camera Master 后执行：python3.12 tools/run.py "
            f"{episode_id} --build"
        )
        return

    if action == "NEED_ASSET":
        scene_id = runtime["current_scene_id"]
        path = episode_dir / "director_state" / scene_id / "ASSET_REQUIREMENT.md"
        try:
            package_dir = build_current_shot_package(episode_id, episode_dir)
        except AssetRequirementError as exc:
            print("\n当前 Shot 缺少必需 Master 资产，生产已暂停。")
            print(exc)
            if path.is_file():
                print(f"Requirement: {path.relative_to(PROJECT_ROOT)}")
        else:
            print("\n资产缺口已解除，Shot Package Generated")
            print(package_dir.relative_to(PROJECT_ROOT))
            print_reference_warnings(package_dir)
        return

    if action == "EPISODE_COMPLETE":
        print("\nEpisode 已完成。")
        return

    print(f"\n当前 next_action: {action}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CatDrama Studio V4.1 Runtime 统一入口。"
    )
    parser.add_argument("episode_id")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="重新 Build Episode，并重建 Director State Skeleton。",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="普通 Build，保留现有 Director State。",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="只显示 Runtime State。",
    )
    parser.add_argument(
        "--apply-director-plan",
        metavar="JSON_PATH",
        help="导入 GPT Director 输出的 Scene_Director_Plan_RESULT.json。",
    )
    parser.add_argument(
        "--apply-director-qa",
        metavar="JSON_PATH",
        help="导入 GPT Director QA 输出的 Director_QA_RESULT.json。",
    )
    parser.add_argument(
        "--apply-camera-match",
        metavar="JSON_PATH",
        help="导入 GPT Director 输出的 Camera_Match_Result.json。",
    )
    parser.add_argument(
        "--approve-image",
        metavar="IMAGE_PATH",
        help="批准当前 Shot 的 Final Image，并进入 Video 阶段。",
    )
    parser.add_argument(
        "--approve-video",
        metavar="VIDEO_PATH",
        help="批准当前 Shot Video，并自动进入 Next Shot / Next Scene。",
    )
    parser.add_argument(
        "--approve-video-only",
        action="store_true",
        help="不复制视频文件，仅标记当前 Shot Video 已完成并推进 Runtime。",
    )
    args = parser.parse_args()

    try:
        episode_id = normalize_episode_id(args.episode_id)

        if args.reset:
            invoke_build(episode_id, reset=True)
        elif args.build:
            invoke_build(episode_id, reset=False)
            episode_dir = PROJECT_ROOT / "episodes" / episode_id
            resume_camera_gap_after_build(episode_id, episode_dir)
        else:
            episode_dir = PROJECT_ROOT / "episodes" / episode_id
            runtime_path = director_state_root(
                episode_dir
            ) / "Runtime_State.json"
            if not runtime_path.is_file():
                invoke_build(episode_id, reset=False)

        if args.apply_director_plan:
            episode_dir = PROJECT_ROOT / "episodes" / episode_id
            result_path = Path(args.apply_director_plan)
            if not result_path.is_absolute():
                result_path = PROJECT_ROOT / result_path
            result, issues = apply_director_plan(
                episode_id,
                episode_dir,
                result_path,
            )
            print(f"Director Plan Import: {result}")
            if issues:
                for item in issues:
                    print(f"- {item}")
            if result != "PASS":
                return 2

        if args.apply_director_qa:
            episode_dir = PROJECT_ROOT / "episodes" / episode_id
            result_path = Path(args.apply_director_qa)
            if not result_path.is_absolute():
                result_path = PROJECT_ROOT / result_path
            result, issues = apply_qa_result(
                episode_id,
                episode_dir,
                result_path,
            )
            print(f"Director QA Import: {result}")
            if issues:
                for item in issues:
                    print(f"- {item}")
            if result == "INVALID_QA_RESULT":
                return 2

        if args.apply_camera_match:
            episode_dir = PROJECT_ROOT / "episodes" / episode_id
            result_path = Path(args.apply_camera_match)
            if not result_path.is_absolute():
                result_path = PROJECT_ROOT / result_path
            result, issues = apply_camera_match(
                episode_id,
                episode_dir,
                result_path,
            )
            print(f"Camera Match Import: {result}")
            if issues:
                for item in issues:
                    print(f"- {item}")
            if result != "PASS":
                return 2

        if args.approve_image:
            episode_dir = PROJECT_ROOT / "episodes" / episode_id
            image_path = Path(args.approve_image)
            if not image_path.is_absolute():
                image_path = PROJECT_ROOT / image_path
            print(f"Image Approved: {approve_image(episode_id, episode_dir, image_path)}")

        if args.approve_video or args.approve_video_only:
            episode_dir = PROJECT_ROOT / "episodes" / episode_id
            video_path = None
            if args.approve_video:
                video_path = Path(args.approve_video)
                if not video_path.is_absolute():
                    video_path = PROJECT_ROOT / video_path
            print(f"Video Approved: {approve_video(episode_id, episode_dir, video_path)}")

        if not any([
            args.status,
            args.approve_image,
            args.approve_video,
            args.approve_video_only,
        ]):
            episode_dir = PROJECT_ROOT / "episodes" / episode_id
            if refresh_stale_current_package_state(episode_id, episode_dir):
                print("旧版未批准 Shot Package 已按 9:16 技术合同重新排队。")

        runtime = load_runtime(episode_id)
        if args.status:
            print_runtime(runtime)
            return 0

        handle_current_action(episode_id)
        return 0

    except Exception as exc:
        print(f"CatDrama Run Failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
