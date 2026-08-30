# CatDrama Studio V4.1 — Production Standard

Version: 4.1

本文件是 V4.1 正式 Production 职责合同。若旧 V2/V4 文档、示例或聊天记忆与本
文件冲突，以本文件和 V4.1 JSON Schema 为准。

## 1. 四层架构

```text
GPT Director Brain
→ Director State JSON
→ Python Runtime / Validator / Compiler / Builder
→ Image / Video Generation
```

### GPT Director Brain

负责 Scene 级创意决策：Shot 数量、Coverage、Composition、Camera、运镜、表演、
Frozen Moment、Shot Delta、Previous Frame Policy、Scene End，以及每镜的
`why_this_shot` / `why_not_previous_shot`。

### Director State JSON

保存 GPT 决策，是跨对话与跨工具的持久化事实。Plan 未通过 Director QA 前不得
编译为正式 Shot State。

### Python 执行层

只允许：Schema 验证、状态转移、确定性字段复制、Prompt 编译、资产完整性验证、
版本化打包、Final 文件登记与 Next Shot / Next Scene 推进。

禁止：新增或合并 Shot、选择 Camera/Coverage、改 Composition、推断 Frozen
Moment、补动作/运镜、根据剧情或聊天上下文重做导演判断。

### Generation 层

只执行当前版本 Package 中已经编译并校验的 IMAGE / VIDEO Prompt。生成失败不
自动证明 Prompt 错误；先按 Package 合同区分模型执行问题和上游 State 问题。

## 2. 权威事实

```text
Director Plan = Shot 设计唯一来源
Shot State    = Prompt 执行唯一来源
Runtime State = 生产进度唯一来源
```

| 事实 | 唯一来源 |
| --- | --- |
| 剧情事件、关键对白、Scene 顺序 | `Confirmed_Script.md` |
| Scene/Shot 创意导演设计 | `Scene_Director_Plan_RESULT.json` |
| Director QA 结论 | `Director_QA_RESULT.json` |
| Prompt 执行内容 | 锁定的 `Shot_State.json` |
| 当前 Scene、Shot、下一动作 | `Runtime_State.json` |
| 资产路径、大小、SHA256 | `assets/AssetRegistry.json` |
| 当前有效 Shot Package | `CURRENT_PACKAGE.json` |

Director Decision 中的“为什么”供 QA 与归因使用。Prompt Compiler 与 Builder
不得读取这些理由重新解释镜头。

## 3. GPT Director 输出合同

Planning 阶段只返回符合 `Scene_Director_Plan.schema.json` 的纯 JSON。不得同时
输出 Markdown 解释、完整 Production Package、IMAGE Prompt 或 VIDEO Prompt。

每个 Shot 必须至少明确：

- 叙事、情绪与信息目的；
- `why_this_shot` 和 `why_not_previous_shot`；
- Coverage、Composition 与可见角色；
- Camera Requirement、显式 Camera 选择、Camera Motion 与理由；
- Start State、Frozen Moment、物理边界与禁止提前状态；
- Shot Delta、End State、Previous Frame Policy；
- `scene_end` 与锁定的 `next_shot`。

可见角色、服装、环境、道具与 Camera Master 必须使用显式 Asset ID。Python 不
根据角色名或文件名猜映射。

## 4. Director QA 合同

QA 必须审核完整 Scene Plan，而不是只看 Shot 摘要。至少检查：

- 每镜是否有独立视觉价值，能否被上一镜吸收；
- 是否存在同构图微动作拆镜；
- Coverage / Camera / Composition 是否服务导演意图；
- Frozen Moment 是否是可生成静态瞬间；
- Shot Delta 是否只描述从 Start 到 End 的运动；
- Previous Frame Policy 与切镜/连续性是否一致；
- `scene_end` 与下一 Scene 衔接是否正确；
- 是否存在未登记 Camera 或其他资产需求。

QA 返回纯 JSON。`PASS` 后 Python 只做确定性编译；`REVISE` 后回到 GPT Director
Planning。Python 不替 QA 修复创意字段。

Camera Gap 修复使用 `Camera_Match_Result.schema.json`。GPT Director 只可为明确的
缺口 Shot 修改 `selected_camera`、`camera_status`、`camera_reason`；Python 负责验证
所选 ID 已登记且已进入当前 Episode Asset Selection、增加 Plan revision，并重新执行
完整 Plan Validation。Camera Match 通过后仍必须重新进行 Director QA。

## 5. Prompt 与 Builder 合同

Pure Prompt Compiler 只消费锁定 Shot State 和确定性的 Previous Frame Policy：

- IMAGE Prompt 只描述 Frozen Moment；不得泄漏 Shot Delta、End State 或运镜。
- VIDEO Prompt 只描述从已锁定起始状态到 End State 的运动。
- 编译结果必须通过 Prompt Contract QA，并记录 State/Prompt SHA256。

Builder 只复制当前 Shot 显式声明的资产。Registry 未登记、源文件缺失、大小或
SHA256 不一致都进入 `NEED_ASSET`。Package 使用 `v001 / v002 / ...`，成功版本
永不覆盖。

## 6. Runtime 合同

合法生产主链：

```text
PLAN_CURRENT_SCENE
→ DIRECTOR_QA_REQUIRED
→ GENERATE_CURRENT_SHOT_PACKAGE
→ WAIT_FOR_IMAGE_APPROVAL
→ WAIT_FOR_VIDEO_APPROVAL
→ Next Shot / Next Scene / EPISODE_COMPLETE
```

`NEED_NEW_CAMERA` 和 `NEED_ASSET` 是阻塞分支。Runtime 只按锁定 State 推进，
不依赖 GPT 记忆。Scene 结束后，下一 Scene 必须进入 `PLANNING`，Shot Count = 0。

Camera 分支为：

```text
NEED_NEW_CAMERA
→ Build / Registry Refresh
→ CAMERA_MATCH_REQUIRED
→ Full Plan Validation
→ DIRECTOR_QA_REQUIRED
```

Python 不从候选 Camera 中自动挑选，也不借 Camera 修复修改其他导演字段。

## 7. 正式操作入口

最低 Python 3.10，官方推荐 Python 3.12。用户日常只运行：

```bash
python3.12 tools/run.py <EPISODE_ID> [ACTION]
```

完整命令见项目根目录 `00_WORKFLOW.md`。
