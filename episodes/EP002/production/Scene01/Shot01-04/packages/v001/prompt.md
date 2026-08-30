# Shot Prompt Package

# ChatGPT Shot Handoff — Scene01 Shot01-04

当前模式：SHOT_PROMPT_ONLY

请严格使用本目录中的：
- IMAGE_PROMPT.md
- VIDEO_PROMPT.md
- UPLOAD_MANIFEST.json
- PROMPT_COMPILATION_MANIFEST.json

规则：
- 只输出 Production Progress、IMAGE PROMPT、VIDEO PROMPT。
- 不调用图片生成。
- 不重新规划 Scene 或 Shot。
- 不改变 Camera / Coverage / Composition。
- 不把 VIDEO 动作提前到 IMAGE。
- Previous Frame Policy: STATE_REFERENCE_ONLY
- 只继承上一镜的 Identity / Space / Lighting / Props / Action State。不上传上一 Final；Camera / Coverage / Composition 以当前 Director Plan 为准。

---

# IMAGE PROMPT

严格执行已经锁定的 Shot State；不得重新导演或补全缺失创意。

## Production Identity
- Episode: EP002
- Scene: Scene01
- Shot: Shot01-04

## Shot Execution
- Primary Function: CHARACTER_REVEAL
- Primary Focus: 阿诺走到小南正前方端正坐下并郑重承诺
- Information Density: HIGH

## Camera / Coverage
- Camera Asset: cameras.entrance-hall-camera01
- Camera Status: MATCH
- Axis Status: PRESERVED
- Coverage: MEDIUM_WIDE
- Composition Intent: 小南在门前形成竖向中心，怀中大漂亮位于上层、腿边小帅位于下层、阿诺在前方地面端正居中，三猫形成围绕小南的层级三角；门保持后景中心，观众第一眼落在阿诺严肃坐姿，随后读到另外两猫的悲伤配合和小南软化的表情。

Camera Motion 只属于 VIDEO；静态 IMAGE 不得表现运镜后的结果。

## Character Visibility
- Visible: 小南, 大漂亮, 小帅, 阿诺
- Partial: None
- Off Screen: None

不得把 Off Screen 角色重新加入画面。

## Continuity
- Mode: CAMERA_CUT_CONTINUITY
- Previous Frame Policy: STATE_REFERENCE_ONLY
- Previous Frame Instruction: 只继承上一镜的 Identity / Space / Lighting / Props / Action State。不上传上一 Final；Camera / Coverage / Composition 以当前 Director Plan 为准。
- Locked Facts: Identity, Space, Lighting, Props, Action State
- Change Allowed: Coverage, Camera, Composition

## Start State
承接 Shot01-03：小南仍在门内抱着大漂亮，小帅前爪贴在小南一侧小腿，阿诺已走到小南正前方附近但仍四爪站立，入户门关闭。

## Frozen Moment — IMAGE 最高动作状态真相
阿诺已经走到小南正前方、即将收腿端正坐下之前的稳定站立瞬间。

### Physical Boundaries
- 阿诺四爪全部接触地面，臀部尚未落地，前腿仍为站立承重状态
- 阿诺与小南之间保留一只猫身长度以内的清楚地面间距
- 大漂亮仍由小南双臂支撑在怀中，没有下地
- 小帅前爪仍贴在小南小腿，后腿与腹部靠近地面承重
- 入户门保持完全关闭

### Forbidden Advanced States
- 阿诺已经端正坐好或已经说出承诺
- 小南已经笑出来或揭示取快递
- 大漂亮已经从怀中下来
- 小帅已经松开前爪
- 入户门已经打开

## Still Image Contract
- IMAGE 必须停在 Frozen Moment。
- 不得执行 Shot Delta、End State 或下一 Shot 动作。
- 不得改变 Identity、Environment、Outfit、Props、Camera、Coverage 或 Composition Intent。
- 不得增加 Shot State 中不存在的角色、动作、道具或空间信息。

---

# VIDEO PROMPT

严格从已批准的 IMAGE Frozen Moment 开始；不得重新导演。

## Production Identity
- Episode: EP002
- Scene: Scene01
- Shot: Shot01-04

## Shot Delta
### Primary Action
阿诺缓慢收腿，在小南正前方端正坐好，抬头以严肃稳定的语气说：“主人放心。我会照顾好他们两个。”

### Secondary Actions
- 大漂亮和小帅继续维持悲伤表情，不新增动作抢戏
- 小南依次看过三只猫，表情由错愕轻微软化，短暂被感动但尚未笑

### Performance Notes
阿诺完全相信自己正在做可靠承诺，语气不得带自知搞笑；小南的感动只持续一拍，为下一镜的生活化拆穿保留反差。

### Timing
- 0.0-1.2秒：阿诺缓慢坐正并抬头
- 1.2-4.8秒：阿诺完成两句承诺
- 4.8-6.5秒：小南看过三猫并短暂感动，保留静默拍点

## Camera Motion
- Movement: LOCKED_OFF
- Movement Reason: 阿诺的笑点依赖端正坐下后像正式负责人一样稳定发言，固定镜头让其严肃姿态与另外两猫的夸张悲伤形成可观察反差。

不得增加 Shot State 中不存在的额外运镜。

## End State
阿诺在小南正前方端正坐好并保持严肃目光；大漂亮仍在怀中，小帅仍抱腿；小南看着三只猫短暂动容，尚未笑或说明真相；门保持关闭。

## Duration
- Estimated Duration: 6.5 seconds

## Continuity Lock
- Mode: CAMERA_CUT_CONTINUITY
- Locked Facts: Identity, Space, Lighting, Props, Action State
- Change Allowed: Coverage, Camera, Composition
- 只执行当前 Shot Delta，不得继续表演下一 Shot。
