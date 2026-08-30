from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from common import BUILD_ROOT, PROJECT_ROOT, normalize_episode_id, read_optional, read_required


CREATIVE_AUTHORITY = """
你是当前 Scene 的 GPT Director。

Studio 提供：
- 已锁定事实
- Master 资产
- 本集目标
- V4.1 Director Plan Schema

镜头节奏、视觉表达、表演调度、场面调度、Shot 拆分、Camera、
Coverage、Composition、Frozen Moment、Shot Delta 与运镜均由你自主决定。

你只负责输出 Scene Director Plan JSON 或 Director QA JSON。
当 Runtime 明确进入 CAMERA_MATCH_REQUIRED 时，只输出 Camera Match Result JSON，
且不得借机修改非 Camera 匹配字段。
IMAGE / VIDEO Prompt 由 Python 从锁定 Shot State 确定性编译，禁止在 Planning
阶段提前生成或改写 Prompt。

不得修改 Confirmed Script 已锁定的故事事实、角色动机和事件顺序。

不要输出内部推理过程。

不要机械套用模板。

所有创作必须保持：
- 角色身份
- 性格核心
- 世界观
- Master 外观
- 场景空间逻辑
- 道具连续性
"""


PRODUCTION_SHOT_RULE = """
V4.1 Director Planning Rules:

Shot 是 AI 视频生产的最小单位。

Scene 是叙事单位。
Shot 是视觉生产单位。

Shot 数量必须由当前 Scene 的导演表达需要决定，不得套用固定数量。

每个 Shot 必须具有：

- why_this_shot
- why_not_previous_shot
- Camera / Coverage / Composition
- Frozen Moment / Physical Boundaries
- Shot Delta / End State
- Previous Frame Policy / Scene End

不得输出 IMAGE Prompt 或 VIDEO Prompt；Python 将在 Plan 通过 QA 后编译。
"""


SESSION_CONTINUITY = """
Runtime State 是当前 Scene、Shot 与下一动作的唯一来源。
不得根据聊天记忆维护生产进度或推断 Next Shot。

已经上传并锁定的 Master 资产无需重复上传。只有资产缺失、替换或无法唯一对应
时，才提出缺失项。
"""


FACTS = (
    ("Creative Guidelines", PROJECT_ROOT / "bible" / "Creative_Guidelines.md"),
    ("Cinematic Guidelines", PROJECT_ROOT / "bible" / "Cinematic_Guidelines.md"),
    ("Characters", PROJECT_ROOT / "bible" / "Character_Bible.md"),
    ("World", PROJECT_ROOT / "bible" / "World_Bible.md"),
    ("Visual Identity", PROJECT_ROOT / "bible" / "Visual_Bible.md"),
    ("Asset Registry", PROJECT_ROOT / "assets" / "AssetRegistry.json"),
)

def section(parts, title, content):
    parts.extend(["", "---", "", f"## {title}", "", content.strip()])


def render_asset_inventory(selection):
    selected = selection.get("selected", [])
    lines = [
        "以下列表与 Asset Registry 中登记资产对应。",
        "AI Director 必须基于这些资产进行 Asset Decision。",
        "禁止创造不存在的 Character、Environment、Camera、Prop。",
        "",
    ]

    if selected:
        for item in selected:
            lines.append(
                f"- `{item['id']}` — {item['name']} — `{item['package_path']}`"
            )
    else:
        lines.append("- 当前没有解析到资产。")

    return "\n".join(lines)


def build_context_pack(episode_id, selection=None, output_dir=None):
    episode_id = normalize_episode_id(episode_id)

    episode_dir = PROJECT_ROOT / "episodes" / episode_id

    if not episode_dir.is_dir():
        raise FileNotFoundError(f"不存在: {episode_dir}")

    if selection is None:
        selection = {
            "selected": [],
            "missing": [],
            "ambiguous": []
        }

    parts = [
        "# CatDrama Studio — Production Context",
        "",
        f"Episode: {episode_id}",
        f"Built: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
        "这是当前单集完整创作环境。",
        "同时上传的资产包是唯一视觉依据。",
    ]

    section(parts, "Creative Authority", CREATIVE_AUTHORITY)

    section(
        parts,
        "V4.1 Production Rules Reference",
        """
V4.1 正式职责合同不在 Context Pack 中重复展开。

请读取：

- Director_Guidelines.md
- Production_Standard.md
- Scene_Director_Plan.schema.json
- Director_QA_Result.schema.json
- Camera_Match_Result.schema.json

其中 Production_Standard.md 定义 GPT / State / Python 的职责边界，JSON Schema
定义唯一允许的结构化输出格式。
"""
    )

    parts.extend([
        "",
        "---",
        "",
        "## Project Truth",
        ""
    ])

    for title, path in FACTS:
        section(parts, title, read_required(path))

    confirmed = read_optional(
        episode_dir / "Confirmed_Script.md"
    )

    if confirmed:
        section(parts, "Confirmed Script", confirmed)
    else:
        section(
            parts,
            "Story Draft",
            read_required(episode_dir / "Story_Draft.md")
        )

    section(
        parts,
        "Creative Brief",
        read_required(episode_dir / "Creative_Brief.md")
    )

    section(
        parts,
        "Available Master Assets",
        render_asset_inventory(selection)
    )

    section(
        parts,
        "Production Shot Rules",
        PRODUCTION_SHOT_RULE
    )

    section(
        parts,
        "Same Conversation Continuity",
        SESSION_CONTINUITY
    )

    section(
        parts,
        "Final Execution Instruction",
        """
你现在是当前 Scene 的 GPT Director。

请在内部完成：

- 剧情理解
- 角色分析
- Scene 节奏设计
- Shot 拆分
- 镜头选择
- Previous Frame Policy 与 Scene End 判断

收到 SCENE_PLANNING_REQUEST.md 时，只输出符合模板和 Schema 的纯 JSON Director
Plan。收到 DIRECTOR_QA_REQUEST.md 时，只输出符合 Schema 的纯 JSON QA Result。
收到 CAMERA_MATCH_REQUEST.md 时，只输出符合 Schema 的纯 JSON Camera Match Result，
只为请求中列出的缺口 Shot 选择当前 Asset Selection 内的 Camera。

禁止：
- 输出内部推理
- 机械罗列景别
- 为增加镜头而增加镜头
- 输出或改写 IMAGE / VIDEO Prompt
- 根据聊天记忆决定当前 Shot

每个 Shot 必须服务：
故事、情绪、喜剧或视觉信息。
"""
    )

    target = output_dir or BUILD_ROOT / episode_id
    target.mkdir(parents=True, exist_ok=True)

    output = target / f"{episode_id}_Context_Pack.md"

    output.write_text(
        "\n".join(parts).rstrip() + "\n",
        encoding="utf-8"
    )

    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("episode_id")
    parser.add_argument("--selection-json", type=Path)

    args = parser.parse_args()

    try:
        selection = None

        if args.selection_json:
            selection = json.loads(
                args.selection_json.read_text(
                    encoding="utf-8"
                )
            )

        output = build_context_pack(
            args.episode_id,
            selection
        )

        print(output)

    except Exception as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
