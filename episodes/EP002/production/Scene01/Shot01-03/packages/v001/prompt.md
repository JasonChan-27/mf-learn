# Shot Prompt Package

# ChatGPT Shot Handoff — Scene01 Shot01-03

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
- Shot: Shot01-03

## Shot Execution
- Primary Function: PERFORMANCE_SHOT
- Primary Focus: 小帅靠近并抱住小南腿部的悲情加码
- Information Density: LOW

## Camera / Coverage
- Camera Asset: cameras.entrance-hall-camera03
- Camera Status: MATCH
- Axis Status: PRESERVED
- Coverage: MEDIUM
- Composition Intent: 小帅位于画面下半部主焦点，后爪和身体重量明确落在地面，双前爪短暂贴住小南一侧小腿；小南只以膝下腿部进入画面形成尺度和依附关系，背景保留门口地垫或鞋柜边缘作为空间锚点。

Camera Motion 只属于 VIDEO；静态 IMAGE 不得表现运镜后的结果。

## Character Visibility
- Visible: 小帅
- Partial: 小南
- Off Screen: 大漂亮, 阿诺

不得把 Off Screen 角色重新加入画面。

## Continuity
- Mode: CAMERA_CUT_CONTINUITY
- Previous Frame Policy: STATE_REFERENCE_ONLY
- Previous Frame Instruction: 只继承上一镜的 Identity / Space / Lighting / Props / Action State。不上传上一 Final；Camera / Coverage / Composition 以当前 Director Plan 为准。
- Locked Facts: Identity, Space, Lighting, Props, Action State
- Change Allowed: Coverage, Camera, Composition

## Start State
承接 Shot01-02：大漂亮仍在小南怀中；小南站在关闭的门内尚未回答；小帅已在小南腿边，四爪着地并仰头，尚未抬起前爪；阿诺在稍后方缓慢靠近。

## Frozen Moment — IMAGE 最高动作状态真相
小帅已来到小南腿边、即将抬起前爪抱腿前的稳定四爪着地状态。

### Physical Boundaries
- 小帅四只爪全部接触门内地面，后腿承重清楚
- 小帅胸腹没有贴住小南腿部，身体与小南小腿之间仍有窄小可见空隙
- 小帅两只前爪尚未离地或搭上小南腿部
- 小南双脚位置不变，裙摆与腿部保持自然垂落
- 入户门保持完全关闭

### Forbidden Advanced States
- 小帅已经双足直立或以人类姿势站立
- 小帅已经抱住腿并说完台词
- 小南已经弯腰安慰小帅或开始回答
- 大漂亮已经从小南怀中下来
- 阿诺已经坐到小南正前方

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
- Shot: Shot01-03

## Shot Delta
### Primary Action
小帅保持后腿和身体重量贴近地面，短暂抬起前爪抱住小南一侧小腿，仰头用颤抖语气说：“主人……如果你回不来了……我们该怎么办呀？”

### Secondary Actions
- 说到“回不来了”时停半拍后再完成后半句
- 小南腿部保持不动，不通过夸张踉跄放大动作

### Performance Notes
小帅是在自信地升级悲情，不是失去常识；动作必须保持真实猫咪短暂扒腿姿态，禁止长时间双足直立和人类式搂抱。

### Timing
- 0.0-0.7秒：小帅四爪着地仰视
- 0.7-1.5秒：前爪贴上小南小腿并稳定身体
- 1.5-5.8秒：完成台词，中间在第二个省略号处留自然停顿
- 5.8-6.5秒：维持悲伤表情等待回应

## Camera Motion
- Movement: LOCKED_OFF
- Movement Reason: 抱腿动作和颤抖台词本身承担升级，固定低机位可让真实接触边界清晰，避免跟拍造成拟人站立或爪部错位。

不得增加 Shot State 中不存在的额外运镜。

## End State
小帅前爪仍贴在小南一侧小腿，后腿承重并仰头保持悲伤表情；大漂亮仍在小南怀中；阿诺已靠近到小南正前方附近但尚未坐下；门仍关闭。

## Duration
- Estimated Duration: 6.5 seconds

## Continuity Lock
- Mode: CAMERA_CUT_CONTINUITY
- Locked Facts: Identity, Space, Lighting, Props, Action State
- Change Allowed: Coverage, Camera, Composition
- 只执行当前 Shot Delta，不得继续表演下一 Shot。
