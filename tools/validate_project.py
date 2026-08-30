from __future__ import annotations

import json
from pathlib import Path

from asset_index import scan_assets
from common import PROJECT_ROOT, confirmed_script_body, detect_episode_stage, read_required

REQUIRED = [
    "catdrama.json",
    "README.md",
    "00_START_HERE.md",
    "bible/Character_Bible.md",
    "bible/World_Bible.md",
    "bible/Visual_Bible.md",
    "bible/Creative_Guidelines.md",
    "director/Production_Standard.md",
    "templates/Story_Draft_Template.md",
    "templates/Creative_Brief_Template.md",
    "templates/Confirmed_Script_Template.md",
]


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED:
        try:
            read_required(PROJECT_ROOT / rel)
        except (FileNotFoundError, ValueError) as exc:
            errors.append(str(exc))

    try:
        scan_assets()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))

    episodes = sorted(path for path in (PROJECT_ROOT / "episodes").glob("EP*") if path.is_dir())
    if not episodes:
        errors.append("episodes/ 下没有单集目录。")

    for episode in episodes:
        for name in ["Creative_Brief.md", "Asset_Selection.md"]:
            try:
                read_required(episode / name)
            except (FileNotFoundError, ValueError) as exc:
                errors.append(str(exc))

        if not (episode / "Story_Draft.md").is_file():
            warnings.append(f"{episode.name} 缺少 Story_Draft.md；构建器将按旧版 Creative Brief 兼容处理。")
        if not (episode / "Confirmed_Script.md").is_file():
            warnings.append(f"{episode.name} 缺少 Confirmed_Script.md；当前会判定为 Draft Stage。")

        try:
            stage = detect_episode_stage(episode)
            if stage == "production" and not confirmed_script_body(episode / "Confirmed_Script.md"):
                errors.append(f"{episode.name} 阶段判断异常。")
        except OSError as exc:
            errors.append(str(exc))

    if warnings:
        print("Validation warnings:")
        for item in warnings:
            print(f"- {item}")

    if errors:
        print("Validation FAILED")
        for item in errors:
            print(f"- {item}")
        return 1

    print(f"Validation OK：{len(episodes)} episode(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
