from __future__ import annotations

import argparse
import json
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

from asset_index import AssetRecord, registry_payload, scan_assets
from asset_selector import parse_selection, resolve_requests
from build_context_pack import build_context_pack
from common import BUILD_ROOT, PROJECT_ROOT, detect_episode_stage, normalize_episode_id
from director_state import initialize_director_state


START_HERE = PROJECT_ROOT / "00_START_HERE.md"
WORKFLOW = PROJECT_ROOT / "00_WORKFLOW.md"


def copy_start_here(output_dir: Path) -> None:
    shutil.copy2(START_HERE, output_dir / "00_START_HERE.md")
    shutil.copy2(WORKFLOW, output_dir / "00_WORKFLOW.md")


def safe_package_name(asset_id: str, suffix: str) -> str:
    return asset_id.replace(".", "__").replace("/", "_") + suffix.lower()


def package_assets(selected: list[dict], output_dir: Path) -> list[dict]:
    package_root = output_dir / "assets"
    packaged = []

    for record in selected:
        source = PROJECT_ROOT / record["path"]
        category_dir = package_root / record["category"]
        category_dir.mkdir(parents=True, exist_ok=True)

        destination = category_dir / safe_package_name(
            record["id"],
            source.suffix
        )

        shutil.copy2(source, destination)

        item = dict(record)
        item["package_path"] = destination.relative_to(output_dir).as_posix()
        packaged.append(item)

    return packaged


def write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def refresh_project_asset_registry(
    records: list[AssetRecord],
    output: Path | None = None,
) -> dict:
    """Persist the same freshly scanned registry used by the Episode build."""
    if not records:
        raise ValueError(
            "assets/ 下未发现可登记的 Master 资产；已停止 Build，"
            "不会用空 Registry 覆盖现有 assets/AssetRegistry.json。"
        )

    registry = registry_payload(records)
    write_json(
        output or PROJECT_ROOT / "assets" / "AssetRegistry.json",
        registry,
    )
    return registry


def write_manifest(episode_id, output_dir, selection, stage):
    lines = [
        f"# {episode_id} V4.1 Director Upload Manifest",
        "",
        f"- Stage: **{stage.upper()}**",
        "",
        "---",
        "",
        "# Package Purpose",
        "",
        "本包用于当前 Scene 的 GPT Director Planning 或 Director QA。",
        "",
        "它不是一次性整集导演稿或 Prompt 生成请求。",
        "",
        "当前 Scene、Shot 与下一动作只以 Runtime State 为准。",
        "",
        "---",
        "",
        "# Story Authority",
        "",
        "Confirmed Script 是唯一剧情真相。",
        "",
        "禁止修改：",
        "",
        "- 故事事件",
        "- 角色动机",
        "- Scene 顺序",
        "- 已确认对白逻辑",
        "",
        "---",
        "",
        "# V4.1 Authority Boundary",
        "",
        "GPT Director 负责 Shot 数量、Camera、Coverage、Composition、Frozen Moment、",
        "Shot Delta、运镜、Previous Frame Policy 与 Scene End。",
        "",
        "Python 只负责 State、验证、确定性编译、资产打包与 Runtime 推进。",
        "",
        "Planning / QA 只返回符合 V4.1 Schema 的纯 JSON。",
        "CAMERA_MATCH_REQUIRED 只返回字段级 Camera Match Result JSON。",
        "不得输出或改写 IMAGE_PROMPT.md / VIDEO_PROMPT.md。",
        "",
        "---",
        "",
        "# Rule References",
        "",
        "正式职责合同与操作流程：",
        "",
        "- Production_Standard.md",
        "- 00_START_HERE.md",
        "",
        "项目导演规范：",
        "",
        "- Director_Guidelines.md",
        "",
        "---",
        "",
        "# Context Sources",
        "",
        "本包包含：",
        "",
        "- Confirmed Script",
        "- Creative Brief",
        "- Character Bible",
        "- World Bible",
        "- Visual Bible",
        "- Asset Registry",
        "- V4.1 State Schema / Runtime / Compiler / Builder Contract",
        "",
        "---",
        "",
        "# Execution Instruction",
        "",
        "先执行 `python3.12 tools/run.py " + episode_id + "` 读取 next_action。",
        "",
        "若为 PLAN_CURRENT_SCENE，请使用 Runtime 生成的 SCENE_PLANNING_REQUEST.md。",
        "",
        "若为 DIRECTOR_QA_REQUIRED，请使用 Runtime 生成的 DIRECTOR_QA_REQUEST.md。",
        "",
        "若为 CAMERA_MATCH_REQUIRED，请使用 Runtime 生成的 CAMERA_MATCH_REQUEST.md。",
        "",
    ]

    path = output_dir / f"{episode_id}_Upload_Manifest.md"
    path.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    return path


def copy_file_to_output(src: Path, output_dir: Path):
    if not src.exists():
        print(f"Skip missing: {src}")
        return

    shutil.copy2(
        src,
        output_dir / src.name
    )

def copy_episode_sources(episode_dir, output_dir, stage):
    source_dir = output_dir / "episode_sources"
    source_dir.mkdir(parents=True, exist_ok=True)

    # 当前 Episode 专属资料
    episode_sources = [
        episode_dir / "Creative_Brief.md",
        episode_dir / "Story_Draft.md",
        episode_dir / "Previous_Episode_Summary.md",
    ]

    if stage == "production":
        episode_sources.insert(
            0,
            episode_dir / "Confirmed_Script.md"
        )

    # 全局共享生产资料
    global_sources = [
        PROJECT_ROOT / "bible" / "Character_Bible.md",
        PROJECT_ROOT / "bible" / "World_Bible.md",
        PROJECT_ROOT / "bible" / "Visual_Bible.md",

        PROJECT_ROOT / "assets" / "AssetRegistry.json",

        PROJECT_ROOT / "director" / "Director_Guidelines.md",
        PROJECT_ROOT / "director" / "Production_Standard.md",

        # V4.1 Director State contracts
        PROJECT_ROOT / "director" / "STATE" / "Scene_Director_Plan.schema.json",
        PROJECT_ROOT / "director" / "STATE" / "Director_QA_Result.schema.json",
        PROJECT_ROOT / "director" / "STATE" / "Camera_Match_Result.schema.json",
        PROJECT_ROOT / "director" / "STATE" / "Director_Decision.schema.json",
        PROJECT_ROOT / "director" / "STATE" / "Scene_Plan.schema.json",
        PROJECT_ROOT / "director" / "STATE" / "Shot_State.schema.json",
        PROJECT_ROOT / "director" / "STATE" / "Runtime_State.schema.json",
        PROJECT_ROOT / "director" / "STATE" / "V4.1_State_Architecture_Delta.md",
        PROJECT_ROOT / "director" / "STATE" / "V4.1_Phase6_Pure_Prompt_Compiler_Contract.md",
        PROJECT_ROOT / "director" / "STATE" / "V4.1_Phase7_Builder_Contract.md",
        PROJECT_ROOT / "director" / "STATE" / "V4.1_Phase9_Stable_Acceptance.md",
        PROJECT_ROOT / "CatDrama_Studio_V4.1_Architecture_Specification.md",
    ]

    # 复制当前 Episode 资料
    for file in episode_sources:
        copy_file_to_output(
            file,
            source_dir
        )

    # 复制全局资料
    for file in global_sources:
        copy_file_to_output(
            file,
            source_dir
        )


def zip_package(episode_id, output_dir):
    target = output_dir / f"{episode_id}_Production_Package.zip"

    with zipfile.ZipFile(
        target,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
    ) as archive:
        for path in sorted(output_dir.rglob("*")):
            if path.is_file() and path != target:
                archive.write(
                    path,
                    path.relative_to(output_dir)
                )

    return target


def build_episode(episode_id, strict=False, clean=True, reset_director_state=False):
    episode_id = normalize_episode_id(episode_id)

    episode_dir = PROJECT_ROOT / "episodes" / episode_id

    if not episode_dir.is_dir():
        raise FileNotFoundError(
            f"剧集目录不存在：{episode_dir}"
        )

    stage = detect_episode_stage(episode_dir)
    if stage != "production":
        raise ValueError(
            "V4.1 Director State 仅在 Confirmed Script 已锁定后初始化。"
        )

    output_dir = BUILD_ROOT / episode_id

    records = scan_assets()
    registry = refresh_project_asset_registry(records)

    initialize_director_state(
        episode_id,
        episode_dir,
        reset=reset_director_state,
    )

    if clean and output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    write_json(
        output_dir / f"{episode_id}_Asset_Registry.json",
        registry
    )

    requests = parse_selection(
        episode_dir / "Asset_Selection.md"
    )

    selected, missing, ambiguous = resolve_requests(
        requests,
        registry["assets"]
    )

    packaged = package_assets(
        selected,
        output_dir
    )

    selection = {
        "schema_version": "4.0",
        "episode": episode_id,
        "stage": stage,
        "selected": packaged,
        "missing": missing,
        "ambiguous": ambiguous,
    }

    write_json(
        output_dir / f"{episode_id}_Asset_Selection.json",
        selection
    )

    build_context_pack(
        episode_id,
        selection=selection,
        output_dir=output_dir
    )

    copy_start_here(output_dir)
    copy_episode_sources(
        episode_dir,
        output_dir,
        stage
    )

    write_manifest(
        episode_id,
        output_dir,
        selection,
        stage
    )

    zip_package(
        episode_id,
        output_dir
    )

    return output_dir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("episode_id")
    parser.add_argument(
        "--reset-director-state",
        action="store_true",
        help="清空并重新建立 V4.1 Director State Skeleton。",
    )

    args = parser.parse_args()

    try:
        output = build_episode(
            args.episode_id,
            reset_director_state=args.reset_director_state,
        )
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
