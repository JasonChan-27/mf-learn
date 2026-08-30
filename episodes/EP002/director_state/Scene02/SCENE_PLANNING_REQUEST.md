# EP002 Scene02 — Scene Director Planning Request

当前为 V4.1 Director Planning 阶段。

当前 Scene：
- Scene：Scene02
- 标题：玄关｜主人离开后的真实状态
- 当前状态：PLANNING
- 当前 Shot 数：0

请严格读取 Production Context Package 中的：

- Confirmed Script
- Creative Brief
- Bible
- Asset Registry / Asset Selection
- Director Guidelines
- V4.1 Architecture Specification
- Scene_Director_Plan.schema.json
- Director_Decision.schema.json
- Camera / Coverage / Continuity 规则（如包内存在）

在内部完成：

1. Scene Director Decision
2. Shot Candidate Planning
3. Director Style Ranking
4. Shot Planning
5. Coverage Planning
6. Camera Planning
7. Planning QA

必须输出一个完整、可直接保存的 JSON 对象。

JSON 必须符合：
director/STATE/Scene_Director_Plan.schema.json

硬性要求：

- 只输出 JSON，不输出 Markdown 代码围栏。
- 不输出 IMAGE PROMPT / VIDEO PROMPT。
- 不输出内部推理。
- Shot 数量由 GPT Director 根据剧情与节奏自主决定，Python 不预设。
- 每个 Shot 必须填写 why_this_shot。
- 每个 Shot 必须填写 why_not_previous_shot。
- 每个 Shot 必须填写 composition_intent。
- Camera / Coverage / Camera Motion / Axis Status 必须由导演决定并说明理由。
- 每个 Shot 必须填写 coverage_reason；Python 不根据 composition_intent 反推理由。
- scene_assets.character_assets 必须由 GPT Director 显式映射角色名到 Character Master ID。
- 每个 visible / partial character 都必须有映射；Python 不会按角色名猜资产。
- frozen_moment.physical_boundaries 必须是可见、可验证的物理边界。
- frozen_moment.forbidden_advanced_states 必须明确禁止首帧提前发生的状态。
- 微小动作变化不得单独拆成新 Shot。
- 最后一镜 scene_end 必须为 true。
- 最后一镜 next_shot 必须明确指向下一 Scene 或 EPISODE_END。
