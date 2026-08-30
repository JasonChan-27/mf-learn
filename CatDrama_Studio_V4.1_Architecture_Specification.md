# CatDrama Studio V4.1 Architecture Specification

版本：V4.1 Draft 1  
状态：架构冻结前设计规范  
目标：彻底分离 **AI 导演创作** 与 **Python 工程执行**  
基线：当前 `CatDrama-Studio(14)` 完整项目

---

# 1. V4.1 的核心结论

CatDrama Studio V4.1 只保留一个最高原则：

> **GPT 负责导演决策；Python 负责状态、验证、编译、打包与推进。**

不得再出现：

```text
Python 根据规则“设计” Shot
Python 自动决定 Camera / Coverage
Python 根据示例 Scene Plan 生成正式镜头
Prompt Compiler 重新理解剧情并改镜头
Runtime 根据聊天上下文猜下一 Shot
```

最终系统固定为四层：

```text
┌──────────────────────────────────────┐
│  1. Director Brain — GPT            │
│  剧情理解 / Scene 导演 / Shot 设计   │
└──────────────────┬───────────────────┘
                   │ Scene Director Plan JSON
                   ▼
┌──────────────────────────────────────┐
│  2. Director State — JSON           │
│  导演决策的唯一持久化事实             │
└──────────────────┬───────────────────┘
                   │ locked state
                   ▼
┌──────────────────────────────────────┐
│  3. Runtime / Validator / Compiler   │
│  Python，只执行，不创作               │
└──────────────────┬───────────────────┘
                   │ Prompt + Upload
                   ▼
┌──────────────────────────────────────┐
│  4. Image / Video Generation        │
│  视觉模型执行已锁定镜头               │
└──────────────────────────────────────┘
```

---

# 2. 当前项目中 V4.1 要纠正的核心问题

当前项目已经拥有：

```text
tools/run.py
tools/director_state.py
tools/state_prompt_compiler.py
tools/build_shot_package.py
director/STATE/*
```

State Runtime 的方向正确。

但当前实现仍存在一个职责越界：

```text
build_episode --reset
→ initialize_episode_director_state
→ Scene01_Plan.example.json
→ 自动将 Scene01 设为 LOCKED
→ 自动产生 Shot01-01 ~ Shot01-04
```

这意味着 Scene01 的：

```text
Shot 数量
Shot Function
Camera
Coverage
Primary Focus
Continuity
```

在 GPT 导演真正工作之前已经被 Python / 示例数据决定。

V4.1 必须取消这一行为。

另外，当前 Shot State 中还存在：

```text
movement_reason: 由 Camera Planner 在正式规划中确认
```

以及较弱的 Frozen Moment：

```text
冻结于当前 Shot 动作正式推进前的可验证稳定状态
```

这类内容说明导演决策并没有完全进入 State。

V4.1 要求：

> Scene 首镜生成前，整个 Scene 的镜头设计必须由 GPT Director 一次性完成并通过 Validator。

---

# 3. GPT 与 Python 的最终职责边界

## 3.1 GPT Director 负责

GPT 是唯一允许进行下列创作判断的模块：

```text
Scene Goal
Audience Experience
Scene Rhythm
Shot Count
Shot Function
Narrative Purpose
Audience Feeling
Primary Focus
Coverage
Camera Requirement
Camera Selection
Camera Selection Reason
Composition Intent
Lens Intent
Camera Motion
Character Visibility
Continuity Mode
Previous Frame Policy
Frozen Moment
Physical Boundaries
Shot Delta
End State
Scene End
Next Scene Entry
```

GPT 必须回答：

> 为什么需要这个 Shot？

以及：

> 为什么上一镜不能继续完成这个功能？

---

## 3.2 Python 负责

Python 只允许执行：

```text
Episode 初始化
Scene Skeleton 建立
Asset Registry
Context Package Build
JSON Schema Validation
Director Plan Validation
State 落盘
Runtime 状态推进
Prompt 编译
Asset Manifest
upload/ 打包
Final Image 审批状态
Scene / Episode 导航
QA Gate 的确定性检查
```

Python 禁止：

```text
决定 Shot 数量
选择 Camera
选择 Coverage
决定景别
决定运镜
设计构图
创造 Frozen Moment
创造 Shot Delta
为了通过 QA 自动改导演方案
```

Python 遇到导演方案不合法时，只能：

```text
FAIL
RETURN_TO_DIRECTOR
NEED_NEW_CAMERA
NEED_ASSET
```

不能自己修。

---

# 4. V4.1 正式数据流

```text
Confirmed Script
        │
        ▼
build_episode
        │
        ├── Episode Context Package
        ├── Asset Reference Map
        └── Scene Skeletons（全部 PLANNING）
        │
        ▼
run.py
        │
        ▼
PLAN_CURRENT_SCENE
        │
        ▼
GPT Director
        │
        ▼
Scene_Director_Plan_RESULT.json
        │
        ▼
Python Director Plan Validator
        │
        ├── FAIL → 返回 GPT Director
        │
        ├── NEED_NEW_CAMERA → 暂停生产
        │
        └── PASS
                │
                ▼
        Director State Compiler
                │
                ├── Scene_Plan.json
                ├── decisions/
                │   └── ShotXX_DirectorDecision.json
                └── shots/
                    └── ShotXX_State.json
                │
                ▼
        Runtime = READY
                │
                ▼
        State Prompt Compiler
                │
                ▼
        prompt.md + required_assets.json + upload/
```

---

# 5. Episode Build 的新职责

## 5.1 `build_episode.py --reset-director-state`

V4.1 中只做：

```text
读取 Confirmed Script
识别 Scene 列表
创建 Director State Skeleton
初始化 Runtime
构建 Context Package
```

所有 Scene 初始必须为：

```json
{
  "plan_status": "DRAFT",
  "status": "PLANNING",
  "shot_count": 0
}
```

包括 Scene01。

---

## 5.2 禁止行为

`build_episode.py` 不得读取：

```text
Scene01_Plan.example.json
```

来生成正式生产计划。

`Scene01_Plan.example.json` 只能：

```text
作为测试 fixture
或 schema 示例
```

必须移动到：

```text
tests/fixtures/
```

或明确重命名：

```text
Scene_Plan.example.json
```

不得进入真实 Episode Runtime。

---

# 6. Director Brain 的正式输入

每次进入新 Scene，Python 生成：

```text
SCENE_PLANNING_REQUEST.md
Scene_Director_Plan_TEMPLATE.json
```

GPT Director 必须读取：

```text
Confirmed Script
Creative Brief
Character Bible
World Bible
Visual Bible
Asset Selection
Asset Reference Map
Camera Registry
Director Brain
Shot Function Library
Director Style Library
Coverage Rules
Camera Planner Rules
Director State Schema
上一 Scene End State（如适用）
```

---

# 7. GPT Director 的唯一正式输出

V4.1 不再要求 GPT 直接输出：

```text
IMAGE PROMPT
VIDEO PROMPT
```

Scene Planning 阶段只允许输出：

```text
Scene_Director_Plan_RESULT.json
```

它是导演创作的完整结果。

---

# 8. Scene Director Plan Schema

建议新的顶层结构：

```json
{
  "schema_version": "4.1",
  "episode_id": "EP002",
  "scene_id": "Scene01",
  "revision": 1,
  "plan_status": "LOCKED",

  "scene_director_decision": {},
  "scene_assets": {},
  "shots": [],
  "scene_end_state": {},
  "next_scene": "Scene02"
}
```

---

# 9. Scene Director Decision

必须包含：

```json
{
  "scene_goal": "",
  "narrative_change": "",
  "primary_character": "",
  "secondary_characters": [],
  "audience_start_state": "",
  "audience_end_state": "",
  "emotion_curve": [],
  "information_curve": [],
  "rhythm_strategy": "",
  "primary_style": "",
  "secondary_style": "",
  "scene_visual_strategy": "",
  "scene_camera_strategy": "",
  "scene_end_intent": ""
}
```

其中：

## `scene_visual_strategy`

不是写具体 Camera。

它描述：

```text
本场视觉注意力如何移动
哪些 Beat 需要空间
哪些 Beat 需要角色反应
什么时候应该降低信息密度
什么时候允许同镜头持续
```

## `scene_camera_strategy`

描述整场摄影原则，例如：

```text
先建立玄关空间；
大漂亮产生反应后立即切离群像；
人猫接触采用互动中景；
Scene End 回到单猫 Reaction，而不是继续群像。
```

它不能是固定公式。

---

# 10. 每个 Shot 的导演字段

每个 Shot 必须包含四层信息。

---

## 10.1 A — Narrative Decision

```json
{
  "shot_id": "Shot01-02",
  "primary_function": "CHARACTER_REVEAL",
  "secondary_effect": "REACTION",

  "narrative_purpose": "让观众第一次明确大漂亮最舍不得小南。",
  "audience_feeling": "由观察转为轻微共情。",
  "information_gain": "大漂亮是三只猫中最先采取行动的角色。",

  "why_this_shot": "当前注意力必须从群像转移到大漂亮。",
  "why_not_previous_shot": "继续保持玄关群像会稀释大漂亮的依恋反应，观众无法清楚读取角色差异。"
}
```

### `why_not_previous_shot`

V4.1 新增强制字段。

这是防止：

```text
Shot01
Shot02
Shot03
```

只是同一画面微调动作的最重要 Gate。

如果 GPT 无法说明：

> 为什么这个功能不能在上一镜完成？

这个 Shot 应被合并。

---

# 11. B — Visual Decision

```json
{
  "primary_focus": "DaPiaoLiang",
  "secondary_focus": "XiaoNan Partial",

  "coverage": "MEDIUM_CLOSE",

  "composition_intent": "大漂亮占主要视觉面积，小南腿部和自然下垂的手只作为关系信息进入边缘，玄关门与鞋柜柔焦保留空间识别。",

  "information_density": "LOW",

  "visible_characters": ["DaPiaoLiang"],
  "partial_characters": ["XiaoNan"],
  "off_screen_characters": ["XiaoShuai", "Arno"]
}
```

Coverage 不只是枚举。

必须有：

```text
composition_intent
```

否则 Python 虽然知道 `MEDIUM_CLOSE`，生成模型仍可能退回群像。

---

# 12. C — Camera Decision

```json
{
  "camera_requirement": {
    "purpose": "Cat Reaction",
    "scale": "MEDIUM_CLOSE",
    "subject_zone": "XiaoNan feet / cat reaction zone",
    "axis_requirement": "Preserve entrance axis",
    "lens_intent": "压缩背景，突出猫咪反应"
  },

  "selected_camera": "cameras.entrance-hall-camera03",
  "camera_status": "MATCH",

  "camera_reason": "Camera03 的固定高度、方向与中近景范围最适合读取单猫情绪，同时保留玄关空间身份。",

  "camera_motion": "LOCKED_OFF",
  "camera_motion_reason": "反应本身是信息重点，运镜会削弱静态情绪读取。"
}
```

---

# 13. Camera Motion 的原则

运镜也是 GPT Director 决策。

允许：

```text
LOCKED_OFF
SLOW_PUSH_IN
SLOW_PULL_OUT
PAN
TILT
TRACK
HANDHELD_MICRO
```

但不得为了“让镜头丰富”机械加入运镜。

每个非 `LOCKED_OFF` Shot 必须有：

```text
camera_motion_reason
```

例如：

```text
SLOW_PUSH_IN
因为观众理解从群像逐渐集中到小南与大漂亮的接触。
```

如果没有叙事理由，则使用 `LOCKED_OFF`。

---

# 14. Lens 设计原则

若 Camera Master 已固定 Lens：

GPT 不得直接改 Lens。

GPT 只输出：

```text
lens_intent
```

Camera Planner 用它选择 Camera。

如果没有 Camera 满足：

```text
coverage
subject_zone
axis
lens_intent
```

则：

```text
camera_status = NEED_NEW_CAMERA
```

流程暂停。

不得：

```text
自动用 Camera01 广景替代
```

---

# 15. D — Temporal / State Decision

这是 V4.1 对图片动作准确性的核心。

```json
{
  "continuity_mode": "CAMERA_CUT_CONTINUITY",
  "previous_frame_policy": "STATE_REFERENCE_ONLY",

  "start_state": {
    "description": ""
  },

  "frozen_moment": {
    "description": "大漂亮起跳前最后一个稳定瞬间。",
    "physical_boundaries": [
      "四只脚全部接触地面",
      "后腿轻微屈曲",
      "前爪尚未离地",
      "胸口尚未进入向上运动",
      "身体尚未接触小南"
    ],
    "forbidden_advanced_states": [
      "前爪离地",
      "身体已经跳起",
      "已经碰到裙摆",
      "已经进入小南怀中"
    ]
  },

  "shot_delta": {
    "primary_action": "从四脚着地启动真实起跳，并向小南靠近。",
    "secondary_actions": [],
    "performance_notes": "",
    "timing": []
  },

  "end_state": {
    "description": ""
  }
}
```

---

# 16. Frozen Moment 必须由 GPT Director 写

Python 不得再根据关键字生成：

```text
四脚着地
前爪离地
```

原因：

不同剧情动作的物理边界无法可靠通过规则猜测。

Python 只能检查：

```text
physical_boundaries 非空
forbidden_advanced_states 非空
```

真正内容由 GPT Director 创作。

---

# 17. Director Decision 与 Execution State 分离

V4.1 不建议 Builder 直接读取所有导演理由。

导入 GPT Plan 后，Python 拆成两种状态。

---

## 17.1 Director Decision

路径：

```text
episodes/EP002/director_state/Scene01/decisions/
├── Shot01-01_DirectorDecision.json
├── Shot01-02_DirectorDecision.json
└── ...
```

保存：

```text
narrative_purpose
audience_feeling
information_gain
why_this_shot
why_not_previous_shot
camera_reason
coverage_reason
camera_motion_reason
```

用途：

```text
Director QA
Scene QA
自动评分
未来重新规划
问题诊断
```

Builder 不需要读取这些理由。

---

## 17.2 Shot Execution State

路径：

```text
shots/Shot01-02_State.json
```

只保存真正执行字段：

```text
primary_function
coverage
composition_intent
primary_focus
visibility
camera_asset
camera_motion
continuity
frozen_moment
shot_delta
end_state
required_assets
scene_end
next_shot
```

Prompt Compiler 只读取它。

---

# 18. 为什么要拆 Director Decision

例如最终图片仍然像上一镜。

系统可以比较：

```text
Director Decision:
why_not_previous_shot =
“需要切离群像，突出大漂亮”
```

与：

```text
Execution:
Camera03
MEDIUM_CLOSE
DaPiaoLiang Primary
```

以及最终 Prompt。

如果 Prompt 最终仍是群像：

```text
问题 = Compiler / Image Generation
```

如果 Director Decision 本身写：

```text
继续保持所有角色完整同框
```

则：

```text
问题 = Director Planning
```

以后错误可以精确定位。

---

# 19. Scene Plan Validator

GPT 返回 JSON 后，Python 必须进行确定性验证。

Validator 不设计镜头，只判断合同是否满足。

---

# 20. Structural Gate

必须：

```text
shot_count == shots.length
Shot ID 连续
最后一个 Shot scene_end == true
next_scene 明确
所有必填字段存在
```

---

# 21. Creative Integrity Gate

每个 Shot 必须包含：

```text
narrative_purpose
audience_feeling
why_this_shot
why_not_previous_shot
composition_intent
camera_reason
frozen_moment
shot_delta
```

空字段直接 FAIL。

---

# 22. Micro-action Gate

若相邻 Shot：

```text
Primary Function 相同
Primary Focus 相同
Coverage 相同
Camera 相同
Composition Intent 高度相同
```

并且新增变化只有：

```text
再走一步
再摸一下
轻微低头
耳朵转动
尾巴轻摆
```

Validator 返回：

```text
MERGE_REQUIRED
```

注意：

Validator 不自动 Merge。

返回 GPT Director 重规划。

---

# 23. Shot Difference Gate

每个 Shot 必须至少在以下维度产生一个**导演意义上的变化**：

```text
Narrative Purpose
Audience Information
Audience Emotion
Primary Focus
Visual Information Density
Action Phase
Relationship Understanding
Expectation
```

仅 Camera 改变不算充分理由。

仅景别改变也不算充分理由。

---

# 24. Coverage / Visibility Gate

例如：

```text
MEDIUM_CLOSE
```

若同时要求：

```text
4 个完整角色
完整环境
多个同等重要动作
```

返回：

```text
FAIL_COVERAGE
```

不允许 Compiler 自己删角色。

---

# 25. Camera Gate

Validator 检查：

```text
selected_camera 是否在 Camera Registry
Camera 是否支持所需 Environment
Camera Role 与 Shot Function 是否明显冲突
Coverage 是否在 Camera 支持范围
```

不匹配：

```text
NEED_NEW_CAMERA
```

---

# 26. Continuity Gate

规则：

```text
Scene 首镜
→ previous_frame_policy 通常 NONE

CAMERA_CUT_CONTINUITY
→ STATE_REFERENCE_ONLY 或 NONE

SAME_CAMERA_CONTINUATION
→ HIGH_PRIORITY_VISUAL_CONTINUITY
```

若：

```text
CAMERA_CUT_CONTINUITY
+
HIGH_PRIORITY_VISUAL_CONTINUITY
```

默认 FAIL，除非 Director Decision 有特殊理由并通过 QA。

---

# 27. Scene Variety Gate

这个 Gate 不是固定要求：

```text
Wide → Medium → Close
```

而是检查 Scene 是否陷入重复。

3 Shot 以上 Scene，若：

```text
所有 Shot Primary Focus 相同
所有 Shot Camera 相同
所有 Shot Coverage 相同
所有 Shot Information Density 相同
```

则返回：

```text
REVIEW_REQUIRED
```

GPT Director 必须说明为何需要长镜头式设计。

如果没有明确理由：

```text
REPLAN_REQUIRED
```

---

# 28. Scene Director QA

Validator 通过结构检查后，再进行 GPT Director QA。

这是第二次 GPT 调用，职责不是重新创作，而是审查完整 Scene Plan。

输入：

```text
Confirmed Script
Scene Director Plan
Camera Registry
Director Guidelines
```

检查：

```text
Narrative completeness
Rhythm
Shot necessity
Shot similarity
Character priority
Coverage diversity
Camera logic
Action continuity
Frozen Moment accuracy
Scene End
```

输出只允许：

```json
{
  "result": "PASS"
}
```

或者：

```json
{
  "result": "REPLAN_REQUIRED",
  "issues": [...]
}
```

只有 PASS 才允许 Python 锁定 State。

---

# 29. V4.1 Runtime 状态机

Episode Runtime：

```text
BUILD_REQUIRED
↓
PLAN_CURRENT_SCENE
↓
DIRECTOR_QA_REQUIRED
↓
GENERATE_CURRENT_SHOT_PACKAGE
↓
WAIT_FOR_IMAGE_APPROVAL
↓
GENERATE_CURRENT_SHOT_PACKAGE
...
↓
PLAN_NEXT_SCENE
↓
EPISODE_COMPLETE
```

---

# 30. `run.py` 的最终职责

`run.py` 是用户唯一入口。

它不得：

```text
自动设计 Scene
自动决定 Shot
自动决定 Camera
```

它只判断：

```text
现在缺什么？
```

---

# 31. 第一次启动 Episode

执行：

```bash
python3.12 tools/run.py EP002 --reset
```

V4.1 正确结果应该是：

```text
Episode Build PASS
Director State Skeleton Created

Current:
Scene01

Next Action:
PLAN_CURRENT_SCENE
```

不应该直接生成：

```text
Shot01-01 prompt.md
```

---

# 32. 规划 Scene

执行：

```bash
python3.12 tools/run.py EP002
```

生成：

```text
Scene01/
├── SCENE_PLANNING_REQUEST.md
├── Scene_Director_Plan_TEMPLATE.json
└── Scene_Director_Plan_RESULT.json
```

用户：

```text
上传 Production Context Package
+
发送 SCENE_PLANNING_REQUEST.md
```

GPT Director 返回纯 JSON。

---

# 33. 导入 Director Plan

```bash
python3.12 tools/run.py EP002 \
  --apply-director-plan \
  episodes/EP002/director_state/Scene01/Scene_Director_Plan_RESULT.json
```

Python：

```text
Schema Validate
↓
Deterministic QA
↓
Director QA Required
```

---

# 34. Director QA

`run.py` 自动生成：

```text
SCENE_DIRECTOR_QA_REQUEST.md
```

用户发送给导演对话。

GPT 返回：

```json
{
  "result": "PASS"
}
```

保存：

```text
Scene_Director_QA_RESULT.json
```

执行：

```bash
python3.12 tools/run.py EP002 \
  --apply-director-qa \
  Scene_Director_QA_RESULT.json
```

PASS 后才：

```text
Scene Plan LOCKED
Shot States CREATED
Runtime = GENERATE_CURRENT_SHOT_PACKAGE
```

---

# 35. Shot Production

随后：

```bash
python3.12 tools/run.py EP002
```

Python 执行：

```text
Shot State
→ Prompt Compiler
→ required_assets.json
→ upload/
→ prompt.md
```

这个阶段不再请求 GPT 做导演决策。

---

# 36. Prompt Compiler 的严格职责

Prompt Compiler 只能做：

```text
State Field
→ Natural Language Prompt
```

例如：

```json
"coverage": "MEDIUM_CLOSE"
```

翻译为：

```text
当前为中近景。
```

它不能判断：

```text
也许 Wide 更好
```

---

# 37. Prompt Compiler 可以做的“语言增强”

允许：

```text
格式化
去重
资产文件名映射
把 JSON 状态写成自然中文
加入固定负面约束
加入 Camera Master Lock
加入 Continuity 说明
```

禁止：

```text
增加剧情动作
改变 Frozen Moment
增加可见角色
改变 Camera
改变 Camera Motion
改变 Composition Intent
```

---

# 38. Builder 的最终职责

`build_shot_package.py` 只负责：

```text
验证当前 Runtime Shot
读取 Shot State
调用 State Prompt Compiler
复制 required assets
按 previous_frame_policy 复制 / 不复制 Final
生成：
  prompt.md
  required_assets.json
  upload/
更新：
  Shot status = PROMPTED
```

---

# 39. Previous Frame 的最终规则

不再由用户决定。

---

## NONE

```text
不进入 upload/
不进入 Prompt References
```

适用于：

```text
Scene Start
Location Change
Time Jump
New Sequence
不需要视觉状态继承的 Cut
```

---

## STATE_REFERENCE_ONLY

进入：

```text
upload/
```

但 Prompt 明确：

```text
只校正：
Identity
Outfit
Space
Lighting
Props
Action State
Spatial Orientation
Eyeline / Axis
```

Camera Master 是：

```text
构图
景别
机位
透视
```

的最高优先级。

---

## HIGH_PRIORITY_VISUAL_CONTINUITY

只用于：

```text
SAME_CAMERA_CONTINUATION
```

锁定：

```text
Camera
Composition
Blocking
Action State
Lighting
```

---

# 40. Image QA 与 Runtime

图片生成后必须由用户确认视觉结果。

保存：

```text
ShotXX-XX_Final.png
```

执行：

```bash
python3.12 tools/run.py EP002 --approve
```

Python 只认为：

```text
用户已经确认画面通过
```

Python 不进行视觉审美判断。

---

# 41. Scene End

最后一镜完成后：

```text
Scene State = COMPLETED
```

Runtime：

```text
Next Scene
→ PLAN_CURRENT_SCENE
```

不会：

```text
自动发明 ShotXX-05
```

---

# 42. Camera Gap

如果 GPT Director 输出：

```text
camera_status = NEED_NEW_CAMERA
```

Scene Plan 不锁定。

Runtime：

```text
NEED_NEW_CAMERA
```

同时生成：

```text
CAMERA_REQUIREMENT.md
```

包含：

```text
Environment
Narrative Purpose
Coverage
Subject Zone
Axis
Lens Intent
Height Intent
Composition Requirement
```

用户创建 Camera Master 后：

```text
Asset Index
Asset Selection
Build Episode
重新运行 Scene Planning / Camera Match
```

不得自动用最近似 Camera 凑合。

---

# 43. Asset Gap

角色、环境、服装、道具缺失同理：

```text
NEED_ASSET
```

先补 Master。

不允许 Prompt 临时设计生产资产。

---

# 44. 目录结构 V4.1

建议：

```text
CatDrama-Studio/

director/
├── BRAIN/
├── PLANNING/
├── STATE/
│   ├── Director_State_Architecture.md
│   ├── Scene_Director_Plan.schema.json
│   ├── Scene_Plan.schema.json
│   ├── Director_Decision.schema.json
│   ├── Shot_State.schema.json
│   └── Runtime_State.schema.json
└── QA/

episodes/
└── EP002/
    ├── Confirmed_Script.md
    ├── Asset_Selection.md
    ├── director_state/
    │   ├── Runtime_State.json
    │   ├── Director_State_Index.json
    │   └── Scene01/
    │       ├── SCENE_PLANNING_REQUEST.md
    │       ├── Scene_Director_Plan_RESULT.json
    │       ├── SCENE_DIRECTOR_QA_REQUEST.md
    │       ├── Scene_Director_QA_RESULT.json
    │       ├── Scene_Plan.json
    │       ├── Scene_State.json
    │       ├── decisions/
    │       │   ├── Shot01-01_DirectorDecision.json
    │       │   └── ...
    │       └── shots/
    │           ├── Shot01-01_State.json
    │           └── ...
    └── production/
```

---

# 45. 需要删除 / 降级的旧逻辑

V4.1 实现时必须处理以下旧行为。

---

## 45.1 删除 Scene01 自动正式规划

当前：

```text
Scene01_Plan.example.json
→ build_episode
→ Scene01 LOCKED
```

改为：

```text
Scene01
→ DRAFT / PLANNING
```

---

## 45.2 降级 `Interactive_Production_Runtime`

旧逻辑中：

```text
上传 ZIP
→ 开始 Shot01-01
→ 继续下一 Shot
```

不再是正式生产入口。

V4.1：

```text
run.py
```

才是唯一 Runtime 真相。

ChatGPT 不负责维护 Current Shot。

---

## 45.3 删除 Context Package 中“继续下一 Shot”导航职责

Context Package 只服务：

```text
Scene Planning
Director QA
```

不再负责 Runtime Shot 导航。

---

## 45.4 Python 不再生成 Frozen Moment 内容

当前 `physical_boundaries_for_shot()` 一类规则必须移出生产路径。

可以保留：

```text
Validator
```

但不得生成真实导演内容。

---

## 45.5 `state_prompt_compiler.py` 保留

但必须成为纯 Compiler。

它只能翻译已经存在于 Shot State 的：

```text
physical_boundaries
composition_intent
camera_motion
shot_delta
```

---

# 46. V4.1 的错误归因体系

以后出现问题，不再统一说“Prompt 不好”。

---

## 画面镜头几乎一样

先看：

```text
Director Decision
```

如果 `why_not_previous_shot` 不成立：

```text
Director Planning 问题
```

如果 Director Decision 要求明显切镜，而 Shot State 已正确：

```text
Compiler / Image Model 问题
```

---

## 动作提前

检查：

```text
Frozen Moment
```

如果 Physical Boundary 本身模糊：

```text
Director Planning 问题
```

如果 State 清楚、Prompt 漏掉：

```text
Compiler 问题
```

如果 Prompt 清楚、图片仍提前：

```text
Image Generation 问题
```

---

## Scene 不知道什么时候结束

检查：

```text
Scene Plan / Runtime
```

不再属于 ChatGPT 上下文问题。

---

# 47. V4.1 QA 层级

```text
Level 1 — JSON Schema QA
Level 2 — Deterministic Planning QA（Python）
Level 3 — Director Scene QA（GPT）
Level 4 — Prompt Contract QA（Python）
Level 5 — Image QA（人工 / 视觉模型）
Level 6 — Scene Production QA
Level 7 — Episode QA
```

每层只解决自己负责的问题。

---

# 48. 最终工作流

```text
新 Episode
    │
    ▼
python3.12 tools/run.py EP002 --reset
    │
    ▼
Scene01 = PLANNING
    │
    ▼
python3.12 tools/run.py EP002
    │
    ▼
生成 SCENE_PLANNING_REQUEST
    │
    ▼
GPT Director 设计完整 Scene
    │
    ▼
Scene_Director_Plan_RESULT.json
    │
    ▼
Python Validate
    │
    ▼
GPT Director QA
    │
    ▼
PASS
    │
    ▼
Python 锁定 Scene / Shot State
    │
    ▼
python3.12 tools/run.py EP002
    │
    ▼
Build Shot Package
    │
    ▼
上传 upload/ + prompt.md
    │
    ▼
生成图片
    │
    ▼
保存 Shot_Final
    │
    ▼
python3.12 tools/run.py EP002 --approve
    │
    ▼
下一 Shot
    │
    ▼
Scene End
    │
    ▼
下一 Scene Planning
```

---

# 49. 用户日常需要记住的命令

最终仍然只保留：

```bash
python3.12 tools/run.py EP002
```

当前图片通过：

```bash
python3.12 tools/run.py EP002 --approve
```

首次 / 整集重置：

```bash
python3.12 tools/run.py EP002 --reset
```

新 Scene 的 GPT 规划与 QA 操作全部由 `run.py` 明确告诉用户下一步发送哪个文件、保存到哪里。

---

# 50. V4.1 实现计划

架构确认后，代码重构按以下顺序执行。

## Phase 1 — State Schema

新增：

```text
Scene_Director_Plan.schema.json
Director_Decision.schema.json
```

升级：

```text
Scene_Plan.schema.json
Shot_State.schema.json
Runtime_State.schema.json
```

---

## Phase 2 — Build / Reset

修改：

```text
director_state.py
build_episode.py
```

目标：

```text
所有 Scene，包括 Scene01，reset 后全部 PLANNING。
```

---

## Phase 3 — Director Plan Import

新增：

```text
director_plan_validator.py
director_plan_compiler.py
```

职责：

```text
GPT Director JSON
→ Validate
→ Director Decisions
→ Shot States
```

---

## Phase 4 — Director QA

新增：

```text
Director QA Request Generator
QA Result Import
```

只有：

```text
PASS
```

才锁 Scene。

---

## Phase 5 — Runtime

修改：

```text
run.py
```

新的状态：

```text
PLAN_CURRENT_SCENE
DIRECTOR_QA_REQUIRED
GENERATE_CURRENT_SHOT_PACKAGE
WAIT_FOR_IMAGE_APPROVAL
NEED_NEW_CAMERA
NEED_ASSET
EPISODE_COMPLETE
```

---

## Phase 6 — Pure Prompt Compiler

修改：

```text
state_prompt_compiler.py
```

删除所有创作性补全。

---

## Phase 7 — Builder

确认：

```text
build_shot_package.py
```

只消费锁定 State。

---

## Phase 8 — Workflow

重写：

```text
00_START_HERE.md
00_WORKFLOW.md
Production Standard
```

只保留 V4.1 正式入口。

---

## Phase 9 — EP002 回归测试

必须从：

```text
Scene01
```

重新让 GPT Director 规划。

验收重点：

```text
Shot 数量不是 Python 预设
Camera / Coverage 是 GPT 决策
每镜都有 why_not_previous_shot
Frozen Moment 是 GPT 设计
Scene01 不再出现连续同构图微动作 Shot
Shot Scene End 正确
Scene02 自动进入 PLANNING
```

---

# 51. V4.1 架构冻结标准

只有满足以下条件，V4.1 才允许进入稳定生产：

```text
1. Python 不创建任何正式 Shot 创意。
2. GPT 不维护 Runtime 当前 Shot。
3. Director Plan 是镜头设计唯一来源。
4. Shot State 是 Prompt 的唯一执行来源。
5. Runtime State 是生产进度唯一来源。
6. Asset Reference Map 是文件名唯一来源。
7. Scene 首镜前完整 Scene Plan 已通过 QA。
8. 每个 Shot 能说明 why_this_shot。
9. 每个 Shot 能说明 why_not_previous_shot。
10. Frozen Moment 拥有可验证物理边界。
11. Previous Frame Policy 由 Director Plan 锁定。
12. Camera Gap 不允许自动降级。
13. Prompt Compiler 不进行导演创作。
14. Scene End 不依赖 ChatGPT 记忆。
15. 用户日常仍只需要 run.py。
```

---

# 52. 最终设计原则

CatDrama Studio 的长期目标不是：

> 让 Python 替代导演。

也不是：

> 让 GPT 同时承担导演、状态机、Builder 和文件系统。

而是：

```text
GPT
负责创造性的导演判断。

JSON
负责保存导演判断。

Python
负责可靠地执行导演判断。

Image / Video Model
负责把导演判断变成画面。
```

这就是 V4.1 的最终边界。

**Director Brain 创作，Director State 记忆，Runtime 执行，Prompt Compiler 翻译。**
