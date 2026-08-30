# Shot Prompt Package

# ChatGPT Shot Handoff — Scene01 Shot01-02

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
- Shot: Shot01-02

## Shot Execution
- Primary Function: PERFORMANCE_SHOT
- Primary Focus: 大漂亮在小南怀中的认真担忧表演
- Information Density: LOW

## Camera / Coverage
- Camera Asset: cameras.entrance-hall-camera02
- Camera Status: MATCH
- Axis Status: PRESERVED
- Coverage: MEDIUM_CLOSE
- Composition Intent: 大漂亮占画面主要视觉面积并位于小南怀中上扬视线，小南的下半张脸、眼神和双臂作为关系框架进入画面；入户门或木质门框以柔焦背景维持玄关身份，小帅与阿诺完全退出画面。

Camera Motion 只属于 VIDEO；静态 IMAGE 不得表现运镜后的结果。

## Character Visibility
- Visible: 大漂亮
- Partial: 小南
- Off Screen: 小帅, 阿诺

不得把 Off Screen 角色重新加入画面。

## Continuity
- Mode: CAMERA_CUT_CONTINUITY
- Previous Frame Policy: STATE_REFERENCE_ONLY
- Previous Frame Instruction: 只继承上一镜的 Identity / Space / Lighting / Props / Action State。不上传上一 Final；Camera / Coverage / Composition 以当前 Director Plan 为准。
- Locked Facts: Identity, Space, Lighting, Props, Action State
- Change Allowed: Coverage, Camera, Composition

## Start State
承接 Shot01-01：大漂亮已经稳定处于小南怀中，身体得到双臂支撑；小南仍站在关闭的入户门内；小帅和阿诺保持上一镜结束位置但在本镜画外。

## Frozen Moment — IMAGE 最高动作状态真相
大漂亮在小南怀中稳定下来、即将开口说“主人……”之前的静止凝视。

### Physical Boundaries
- 大漂亮胸腹由小南双臂稳定支撑，身体没有继续上升或下落
- 大漂亮前爪自然搭在小南手臂附近，没有挥爪或触碰小南面部
- 大漂亮嘴部闭合，视线向上落在小南脸部
- 小南双脚仍在门内地面，抱持姿势稳定，身体没有朝门外移动
- 入户门完全关闭

### Forbidden Advanced States
- 大漂亮已经开始或已经说完离别台词
- 小南已经笑出声或开始回答
- 小帅已经抱住小南腿部并进入本镜画面
- 阿诺已经坐到小南正前方
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
- Shot: Shot01-02

## Shot Delta
### Primary Action
大漂亮保持被抱住的真实猫咪姿态，认真仰视小南并说：“主人……外面的世界竞争太激烈了。你一定要注意安全。”

### Secondary Actions
- 小南先轻微睁大眼并停顿，没有立刻回应
- 大漂亮在句尾维持担忧凝视，不追加夸张肢体动作

### Performance Notes
大漂亮的情绪投入必须真诚而非故意搞怪；以眼神、耳位和稳定姿态表演，不做拟人式手势。小南只给克制的意外反应。

### Timing
- 0.0-0.6秒：怀中静止凝视
- 0.6-5.1秒：大漂亮自然完成两句台词
- 5.1-5.8秒：保留小南发愣与大漂亮认真等待的半拍

## Camera Motion
- Movement: LOCKED_OFF
- Movement Reason: 台词的笑点来自大漂亮过度认真的静态凝视与小南半拍发愣，锁定画面比推近更能保留克制观察感。

不得增加 Shot State 中不存在的额外运镜。

## End State
大漂亮仍被小南稳稳抱住并保持担忧目光；小南由意外进入短暂迟疑，尚未回答；门仍关闭，小帅即将从画外抱腿。

## Duration
- Estimated Duration: 5.8 seconds

## Continuity Lock
- Mode: CAMERA_CUT_CONTINUITY
- Locked Facts: Identity, Space, Lighting, Props, Action State
- Change Allowed: Coverage, Camera, Composition
- 只执行当前 Shot Delta，不得继续表演下一 Shot。
