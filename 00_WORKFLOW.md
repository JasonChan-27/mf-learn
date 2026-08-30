# CatDrama Studio V4.1 — Official Workflow

本文件定义唯一正式生产流程。旧 V2/V4 的“一次性生成整集导演稿与 Prompt”流程
不再使用。

## 1. 权威层级

```text
Confirmed Script
→ GPT Scene Director Plan JSON
→ Python Validation
→ GPT Director QA JSON
→ Locked Director / Scene / Shot State
→ Pure Prompt Compiler
→ Versioned Shot Package Builder
→ Image / Video Approval
→ Runtime Next Shot / Next Scene
```

三项唯一事实：

- Director Plan：Shot 创意设计唯一来源。
- Shot State：IMAGE / VIDEO Prompt 唯一执行来源。
- Runtime State：当前 Scene、当前 Shot与下一动作唯一来源。

## 2. 命令规范

最低支持 Python 3.10，推荐 Python 3.12。为避免系统 `python3` 指向旧版本，
官方示例统一使用：

```bash
python3.12 tools/run.py <EPISODE_ID> [ACTION]
```

`tools/run.py` 是唯一日常入口。其他工具是内部模块，不作为用户工作流入口。

## 3. Build、Reset 与 Status

普通 Build 会先扫描 `assets/` 并重写项目级 `assets/AssetRegistry.json`，再刷新
Episode Production Package，同时保留 Director State。空资产扫描不会覆盖原 Registry：

```bash
python3.12 tools/run.py EP002 --build
```

查看状态但不推进：

```bash
python3.12 tools/run.py EP002 --status
```

按 Runtime 当前状态继续：

```bash
python3.12 tools/run.py EP002
```

Reset 只在确定要放弃当前 Director State 时使用：

```bash
python3.12 tools/run.py EP002 --reset
```

Reset 的确定性结果：

- 创建 Runtime State 与全部 Scene Skeleton；
- Scene01 = `PLANNING`；
- `current_shot_id` 为空；
- Shot Count = 0；
- `next_action = PLAN_CURRENT_SCENE`；
- 不创建 Shot、Camera、Coverage、Composition 或 Prompt。

## 4. Scene Director Planning

当 `next_action = PLAN_CURRENT_SCENE`，Runtime 会生成：

```text
episodes/<EP>/director_state/<Scene>/SCENE_PLANNING_REQUEST.md
episodes/<EP>/director_state/<Scene>/Scene_Director_Plan_TEMPLATE.json
```

操作：

1. 上传最新 Production Package。
2. 将 `SCENE_PLANNING_REQUEST.md` 的完整内容交给 GPT Director。
3. GPT Director 只返回符合 Schema 的纯 JSON。
4. 保存为 `Scene_Director_Plan_RESULT.json`。
5. 导入：

```bash
python3.12 tools/run.py EP002 --apply-director-plan episodes/EP002/director_state/Scene01/Scene_Director_Plan_RESULT.json
```

GPT Director 必须显式决定 Shot 数量、Camera、Coverage、Composition、Frozen
Moment、Shot Delta、Previous Frame Policy、`why_this_shot`、
`why_not_previous_shot` 与 `scene_end`。Python 只校验并保存。

## 5. Director QA

Plan 导入成功后，Runtime 进入 `DIRECTOR_QA_REQUIRED` 并生成
`DIRECTOR_QA_REQUEST.md`。把完整 Request 交给 GPT Director QA，保存返回的纯
JSON，然后执行：

```bash
python3.12 tools/run.py EP002 --apply-director-qa episodes/EP002/director_state/Scene01/Director_QA_RESULT.json
```

- QA `PASS`：Python 将已审核 Plan 编译为锁定的 Scene Plan、Director Decision
  与 Shot State，然后进入当前 Shot 生产。
- QA `REVISE`：返回 Scene Planning，由 GPT 修改 Director Plan；Python 不替
  Director 修稿。

## 6. Shot Package

当 `next_action = GENERATE_CURRENT_SHOT_PACKAGE`，运行：

```bash
python3.12 tools/run.py EP002
```

Builder 只读取锁定 Runtime、Scene State、Shot State、Asset Registry，以及被
Previous Frame Policy 明确要求的上一 Final。输出路径：

```text
episodes/<EP>/production/<Scene>/<Shot>/packages/v001/
```

相同输入复用当前完整版本；输入改变或 Package 损坏时创建 `v002`、`v003`，
绝不覆盖旧成功版本。`CURRENT_PACKAGE.json` 指向有效版本。

Package 内的 `IMAGE_PROMPT.md` 与 `VIDEO_PROMPT.md` 是纯 State 编译结果，
不得让 GPT 重新导演或重写它们。只上传 `UPLOAD_MANIFEST.json` 明确列出的当前
Shot 参考资产。

## 7. Image 与 Video Approval

图片人工验收通过后：

```bash
python3.12 tools/run.py EP002 --approve-image <final-image-path>
```

视频人工验收通过后：

```bash
python3.12 tools/run.py EP002 --approve-video <video-path>
```

若不保存视频文件、仅推进 Runtime：

```bash
python3.12 tools/run.py EP002 --approve-video-only
```

Video Approval 后 Python 只按锁定的 `next_shot` / `scene_end` 推进。它不会根据
生成结果或聊天上下文创造下一 Shot。Scene 结束后，下一 Scene 自动进入
`PLANNING`，Shot Count 重新为 0，等待 GPT Director 规划。

## 8. 阻塞状态

### NEED_NEW_CAMERA

根据 `CAMERA_REQUIREMENT.md` 制作新的 Camera Master，并写入
`assets/cameras/`，同时把新 Camera 加入当前 Episode 的 `Asset_Selection.md`。
不要手工编辑 `assets/AssetRegistry.json`。然后执行：

```bash
python3.12 tools/run.py EP002 --build
```

Build 会刷新 Registry、Asset Selection 与 Production Package，但保留原完整
`Scene_Director_Plan_RESULT.json`。Runtime 进入 `CAMERA_MATCH_REQUIRED` 并生成：

```text
episodes/<EP>/director_state/<Scene>/CAMERA_MATCH_REQUEST.md
episodes/<EP>/director_state/<Scene>/Camera_Match_Result_TEMPLATE.json
```

把最新 Production Package 和 `CAMERA_MATCH_REQUEST.md` 交给 GPT Director。它只
为缺口 Shot 选择 Camera、填写 Camera Status 与 Camera Reason，不得改 Shot 数量、
Coverage、Composition、Motion、Axis、Continuity 或动作。保存纯 JSON 后导入：

```bash
python3.12 tools/run.py EP002 --apply-camera-match episodes/EP002/director_state/Scene01/Camera_Match_Result.json
```

Python 只验证 Camera ID 已登记且已被当前 Episode 选择，然后确定性回填三个 Camera
字段并把 Plan revision 加一。完整 Plan Validation 通过后必须重新进入
`DIRECTOR_QA_REQUIRED`。如果仍有 Camera Gap，继续停在 `NEED_NEW_CAMERA`；如果出现
其他 Plan 问题，才回到完整 Scene Planning。

V4.1.0 曾把 Build 后的 Camera Gap 直接退回 `PLAN_CURRENT_SCENE`。V4.1.1 可识别
该旧状态；升级后再执行一次 `--build` 即可恢复到字段级 Camera Match，不必重做整场。

### NEED_ASSET

根据 `ASSET_REQUIREMENT.md` 补齐精确 Master 并刷新：

```bash
python3.12 tools/run.py EP002 --build
```

Builder 会重新验证 Registry 路径、文件大小与 SHA256。缺失、歧义或内容不一致
仍然阻塞，且不会从旧 `build/` 目录寻找替代副本。

## 9. 禁止的旧工作流

- 不直接运行内部 Python 工具推进生产。
- 不让 Python 从示例 Plan 创建正式 Shot。
- 不让 GPT 维护“当前 Shot”或记住下一步。
- 不要求 GPT 一次性输出整集 Scene → Shot → Prompt。
- 不让 Prompt Compiler 或 Builder补 Camera、Composition、动作或运镜。
- 不在 Shot Package 外临时补充创意 Prompt。
