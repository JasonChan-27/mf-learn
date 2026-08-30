# Shot Prompt Package

# ChatGPT Shot Handoff — Scene01 Shot01-06

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
- Shot: Shot01-06

## Shot Execution
- Primary Function: COMEDY_TIMING_SHOT
- Primary Focus: 三只猫集体僵住后收回离别表演
- Information Density: HIGH

## Camera / Coverage
- Camera Asset: cameras.entrance-hall-camera01
- Camera Status: MATCH
- Axis Status: PRESERVED
- Coverage: MEDIUM_WIDE
- Composition Intent: 回到 Camera01 的门内正向构图：小南在门前，大漂亮仍在怀中起始，小帅位于腿边，阿诺在正前方端坐；先让三猫的僵硬层级占据注意力，随后小南与门的动作成为中心。门关闭后，三猫留在室内前中景，形成通向 Scene02 的最终画面。

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
承接 Shot01-05 真相落地后的第一拍：小南仍在关闭的门内抱着大漂亮；大漂亮表情僵住；小帅前爪仍贴在小南小腿且停止表演；阿诺仍在正前方端正坐着并保持严肃。

## Frozen Moment — IMAGE 最高动作状态真相
“只是取个快递”真相落地后，三只猫同时僵住且尚未撤回任何表演动作的集体静止瞬间。

### Physical Boundaries
- 大漂亮仍完整处于小南怀中，四爪尚未回到地面
- 小帅前爪仍贴在小南一侧小腿，尚未松开，后腿仍在地面承重
- 阿诺臀部与前爪稳定接触地面，保持端正坐姿
- 小南双脚仍在门内，抱持大漂亮，手尚未移向门把手
- 入户门完全关闭

### Forbidden Advanced States
- 大漂亮已经下地或转身离开
- 小帅已经松开前爪或跑开
- 阿诺已经起身或放松趴下
- 小南已经打开门、说完叮嘱或走到门外
- 入户门已经再次关闭且小南已在门外

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
- Shot: Shot01-06

## Shot Delta
### Primary Action
保持一拍集体尴尬后，大漂亮慢慢从小南怀中回到地面，小帅松开前爪恢复四爪着地，阿诺仍维持严肃端坐；小南转向门、打开门，在跨出前回头说：“在家乖一点。”随后走出并从外侧把门完全关上。

### Secondary Actions
- 三只猫在收回动作时互不对视，不用额外对白解释尴尬
- 门打开时三只猫都留在门内，不跟随小南跨过门槛
- 门关闭后保留三只猫在屋内面对门的稳定状态

### Performance Notes
先让静默足够落下笑点，再以慢半拍、尽量若无其事的撤回制造尴尬；阿诺不崩掉严肃姿态。小南的叮嘱自然宠溺，不强化胜负感。

### Timing
- 0.0-1.2秒：三猫集体僵住，空气安静
- 1.2-3.6秒：大漂亮下地，小帅松爪，阿诺保持端坐
- 3.6-5.3秒：小南转身并打开门
- 5.3-6.7秒：小南回头说“在家乖一点。”
- 6.7-8.2秒：小南跨出并把门完全关上
- 8.2-8.8秒：三猫留在门内，门关闭，保持短暂静止

## Camera Motion
- Movement: LOCKED_OFF
- Movement Reason: 尴尬笑点依赖空气凝固和角色缓慢撤回，固定机位能把停顿留给观众；门的关闭也无需跟随即可清楚完成。

不得增加 Shot State 中不存在的额外运镜。

## End State
入户门已经从外侧完全关闭，小南位于门外且不再可见；大漂亮四爪着地靠近原抱持位置，小帅四爪着地靠近原腿边位置，阿诺仍在门前端正坐着；三只猫留在屋内面对关闭的门，Scene02 可从同一空间的安静状态直接开始。

## Duration
- Estimated Duration: 8.8 seconds

## Continuity Lock
- Mode: CAMERA_CUT_CONTINUITY
- Locked Facts: Identity, Space, Lighting, Props, Action State
- Change Allowed: Coverage, Camera, Composition
- 只执行当前 Shot Delta，不得继续表演下一 Shot。
