# Shot Prompt Package

# ChatGPT Shot Handoff — Scene01 Shot01-05

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
- Shot: Shot01-05

## Shot Execution
- Primary Function: EMOTIONAL_SHOT
- Primary Focus: 小南从动容到忍笑并温柔揭示只是取快递
- Information Density: LOW

## Camera / Coverage
- Camera Asset: cameras.entrance-hall-camera02
- Camera Status: MATCH
- Axis Status: PRESERVED
- Coverage: MEDIUM_CLOSE
- Composition Intent: 小南面部与大漂亮头部形成上下双焦点，小南一只手从抱持位置移到大漂亮头顶；门的木质色块柔焦留在背景，脚边小帅和地面阿诺均不进入画面，视线重点保持在小南的克制笑意。

Camera Motion 只属于 VIDEO；静态 IMAGE 不得表现运镜后的结果。

## Character Visibility
- Visible: 小南, 大漂亮
- Partial: None
- Off Screen: 小帅, 阿诺

不得把 Off Screen 角色重新加入画面。

## Continuity
- Mode: CAMERA_CUT_CONTINUITY
- Previous Frame Policy: STATE_REFERENCE_ONLY
- Previous Frame Instruction: 只继承上一镜的 Identity / Space / Lighting / Props / Action State。不上传上一 Final；Camera / Coverage / Composition 以当前 Director Plan 为准。
- Locked Facts: Identity, Space, Lighting, Props, Action State
- Change Allowed: Coverage, Camera, Composition

## Start State
承接 Shot01-04：小南仍站在关闭的门内抱着大漂亮，表情刚刚软化；小帅在腿边抱住一侧小腿，阿诺正前方端坐但在本镜画外。

## Frozen Moment — IMAGE 最高动作状态真相
小南被三猫打动一秒、笑意尚未明显出现且手尚未开始摸大漂亮头部的稳定瞬间。

### Physical Boundaries
- 大漂亮仍由小南一侧手臂和身体稳定支撑，身体没有下落
- 小南准备摸头的手仍停在大漂亮头顶之外，手掌与毛发之间有可见空隙
- 小南嘴唇闭合，尚未说“你们三个……”
- 大漂亮头部朝向小南，耳朵和眼神保持认真等待
- 入户门保持完全关闭

### Forbidden Advanced States
- 小南已经明显大笑或已经说完取快递真相
- 小南的手已经接触并完成摸头
- 大漂亮已经从怀中下来
- 小帅已经松开小南腿部
- 阿诺已经改变端正坐姿
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
- Shot: Shot01-05

## Shot Delta
### Primary Action
小南的感动只维持一拍，随后忍不住轻轻笑出来，说：“你们三个……”；她温柔摸了摸大漂亮的头，再自然说明：“我只是出去取个快递。很快回来。”

### Secondary Actions
- 大漂亮在被摸头时保持安静，听到“取个快递”后眼神停住但尚未下地
- 画外的小帅和阿诺不发声，为真相落地留出静默

### Performance Notes
小南不是嘲笑三只猫，而是被关心后觉得它们演得太过；笑意温柔克制。真相台词保持生活口语，不做包袱式重音。

### Timing
- 0.0-0.8秒：小南动容停顿
- 0.8-2.2秒：忍笑并说“你们三个……”
- 2.2-3.3秒：完成一次自然摸头
- 3.3-6.3秒：说完“我只是出去取个快递。很快回来。”
- 6.3-7.0秒：小南与大漂亮保持静止，让真相落地

## Camera Motion
- Movement: LOCKED_OFF
- Movement Reason: 小南先动容、再忍笑、最后平静揭示的表演需要稳定观察，额外推近会把生活化反差处理得过度煽情。

不得增加 Shot State 中不存在的额外运镜。

## End State
小南已经说明只是取快递并停止摸头，仍抱着大漂亮；大漂亮表情僵住，小帅仍抱腿但在画外停住，阿诺仍端坐且保持严肃；门依旧关闭。

## Duration
- Estimated Duration: 7.0 seconds

## Continuity Lock
- Mode: CAMERA_CUT_CONTINUITY
- Locked Facts: Identity, Space, Lighting, Props, Action State
- Change Allowed: Coverage, Camera, Composition
- 只执行当前 Shot Delta，不得继续表演下一 Shot。
