from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from common import PROJECT_ROOT, normalize_episode_id
except ImportError as exc:
    raise SystemExit(
        "无法导入 tools/common.py。请将本文件保存为 tools/init_episode.py，并从项目根目录执行。"
    ) from exc


EPISODES_ROOT = PROJECT_ROOT / "episodes"
TEMPLATES_ROOT = PROJECT_ROOT / "templates"

TEMPLATE_MAP = {
    "Story_Draft.md": "Story_Draft_Template.md",
    "Creative_Brief.md": "Creative_Brief_Template.md",
    "Confirmed_Script.md": "Confirmed_Script_Template.md",
}

ASSET_SELECTION_TEMPLATE = """# {episode_id} Asset Selection

从 `assets/AssetRegistry.json` 复制本集需要使用的资产 `id`，格式如下：

```text
- asset:<id>
```

## Characters

## Environments

## Cameras

## Props

## Outfits
"""

PREVIOUS_EPISODE_TEMPLATE = """# Previous Episode Summary

{summary}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "初始化单集创作目录；不创建 Director State。生成 Story_Draft.md、Creative_Brief.md、"
            "Confirmed_Script.md、Asset_Selection.md 和上一集摘要。"
        )
    )
    parser.add_argument("episode_id", help="集编号，例如 EP002")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的初始化文件。")
    parser.add_argument(
        "--without-previous-summary",
        action="store_true",
        help="不生成 Previous_Episode_Summary.md。",
    )
    return parser.parse_args()


def load_template(template_name: str, episode_id: str) -> str:
    path = TEMPLATES_ROOT / template_name
    if not path.is_file():
        raise FileNotFoundError(f"缺少模板文件：{path.relative_to(PROJECT_ROOT)}")
    content = path.read_text(encoding="utf-8-sig").replace("EPXXX", episode_id)
    return content.rstrip() + "\n"


def previous_episode_summary(episode_id: str) -> str:
    number = int(episode_id[2:])
    if number == 1:
        return f"{episode_id} 为第一集，无上一集连续性。"
    previous_id = f"EP{number - 1:0{len(episode_id) - 2}d}"
    return (
        f"请填写 {previous_id} 结束时必须延续到 {episode_id} 的事实。\n\n"
        "没有连续性要求时，可写：无必须延续的上一集状态。"
    )


def safe_write(path: Path, content: str, force: bool) -> str:
    existed = path.exists()
    if existed and not force:
        return "skipped"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return "overwritten" if existed else "created"


def initialize_episode(
    episode_id: str,
    *,
    force: bool = False,
    include_previous_summary: bool = True,
) -> tuple[Path, list[tuple[Path, str]]]:
    episode_id = normalize_episode_id(episode_id)
    episode_dir = EPISODES_ROOT / episode_id
    episode_dir.mkdir(parents=True, exist_ok=True)

    results: list[tuple[Path, str]] = []
    for output_name, template_name in TEMPLATE_MAP.items():
        path = episode_dir / output_name
        results.append((path, safe_write(path, load_template(template_name, episode_id), force)))

    asset_selection = episode_dir / "Asset_Selection.md"
    results.append(
        (
            asset_selection,
            safe_write(
                asset_selection,
                ASSET_SELECTION_TEMPLATE.format(episode_id=episode_id),
                force,
            ),
        )
    )

    if include_previous_summary:
        previous_summary = episode_dir / "Previous_Episode_Summary.md"
        results.append(
            (
                previous_summary,
                safe_write(
                    previous_summary,
                    PREVIOUS_EPISODE_TEMPLATE.format(summary=previous_episode_summary(episode_id)),
                    force,
                ),
            )
        )
    return episode_dir, results


def main() -> int:
    args = parse_args()
    try:
        episode_dir, results = initialize_episode(
            args.episode_id,
            force=args.force,
            include_previous_summary=not args.without_previous_summary,
        )
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    print(f"Episode initialized: {episode_dir.relative_to(PROJECT_ROOT)}")
    labels = {
        "created": "CREATED",
        "overwritten": "OVERWRITTEN",
        "skipped": "SKIPPED (already exists)",
    }
    for path, status in results:
        print(f"- {labels[status]}: {path.relative_to(PROJECT_ROOT)}")

    episode_id = normalize_episode_id(args.episode_id)
    print("\nNext:")
    print(f"1. Fill in episodes/{episode_id}/Story_Draft.md")
    print(f"2. Fill in episodes/{episode_id}/Creative_Brief.md")
    print(f"3. Fill in episodes/{episode_id}/Asset_Selection.md")
    print(f"4. Confirm Script 后运行: python3.12 tools/run.py {episode_id} --reset")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
