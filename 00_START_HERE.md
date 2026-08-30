# CatDrama Studio V4.1 — START HERE

本文件是 V4.1 Production Package 的正式入口。

## 先确认职责边界

- GPT Director 负责 Scene 的 Shot 数量、Camera、Coverage、Composition、Frozen Moment、Shot Delta、运镜与导演理由。
- Python 只负责 State、Schema 验证、确定性编译、资产校验、版本化 Builder、文件 IO 与 Runtime 推进。
- Director Plan 是 Shot 设计唯一来源；Shot State 是 Prompt 执行唯一来源；Runtime State 是进度唯一来源。
- Python 不补镜头、不猜 Camera、不选替代资产，也不根据聊天记忆决定下一步。

## 运行环境

- 最低 Python：3.10
- 推荐并作为官方命令使用：Python 3.12
- 所有命令都在项目根目录执行。

不要直接运行 `build_episode.py`、`director_plan_importer.py`、
`state_prompt_compiler.py` 或 `build_shot_package.py`。日常唯一入口是：

```bash
python3.12 tools/run.py EP002
```

将 `EP002` 替换为当前 Episode ID。

## 第一次进入或普通刷新

```bash
python3.12 tools/run.py EP002 --build
python3.12 tools/run.py EP002
```

`--build` 会先扫描 `assets/` 并重写项目级 `assets/AssetRegistry.json`，再刷新
Episode Production Package，同时保留现有 Director State。若没有扫描到任何 Master，
Build 会停止并保留原 Registry。普通运行会读取 `Runtime_State.json` 并打印当前唯一
`next_action`。

只有明确要丢弃当前导演状态、从 Scene01 重新规划时才执行：

```bash
python3.12 tools/run.py EP002 --reset
```

`--reset` 会重建 Runtime 与 Scene Skeleton；Scene01 回到 `PLANNING`，Shot Count
为 0。它不会由 Python 生成任何 Shot。

## 按 next_action 工作

| `next_action` | 你要做的事 |
| --- | --- |
| `PLAN_CURRENT_SCENE` | 将 `SCENE_PLANNING_REQUEST.md` 交给 GPT Director；把纯 JSON 保存为 `Scene_Director_Plan_RESULT.json` 后导入。 |
| `CAMERA_MATCH_REQUIRED` | 将 `CAMERA_MATCH_REQUEST.md` 交给 GPT Director；只返回缺口 Shot 的 Camera 映射并导入，不重做整场规划。 |
| `DIRECTOR_QA_REQUIRED` | 将生成的 `DIRECTOR_QA_REQUEST.md` 交给 GPT Director QA；保存纯 JSON 结果后导入。 |
| `GENERATE_CURRENT_SHOT_PACKAGE` | 再运行统一入口；Builder 会从锁定 Shot State 生成当前 Shot 的版本化 Package。 |
| `WAIT_FOR_IMAGE_APPROVAL` | 使用 Package 的 IMAGE Prompt 与 `UPLOAD_MANIFEST.json` 生产图片；人工审核后批准 Final Image。 |
| `WAIT_FOR_VIDEO_APPROVAL` | 使用锁定 VIDEO Prompt 与已批准图片生产视频；人工审核后批准。 |
| `NEED_NEW_CAMERA` | 按 `CAMERA_REQUIREMENT.md` 新建 Camera Master、加入 `Asset_Selection.md` 并执行 `--build`；Python 随后生成 Camera Match Resume 请求，但不自动换机位。 |
| `NEED_ASSET` | 按 `ASSET_REQUIREMENT.md` 补齐精确 Master；禁止相似资产替代。 |
| `EPISODE_COMPLETE` | 当前 Episode 已完成。 |

具体命令与完整状态流见 `00_WORKFLOW.md`。正式职责合同见
`director/Production_Standard.md`。
