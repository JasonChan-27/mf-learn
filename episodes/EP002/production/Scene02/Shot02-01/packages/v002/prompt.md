# Shot Prompt Package

# ChatGPT Shot Handoff — Scene02 Shot02-01

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
- 固定输出 9:16 / PORTRAIT / 1080x1920。
- Previous Frame Policy: STATE_REFERENCE_ONLY
- 只继承上一镜的 Identity / Space / Lighting / Props / Action State。不上传上一 Final；Camera / Coverage / Composition 以当前 Director Plan 为准。

---

# IMAGE PROMPT

严格执行已经锁定的 Shot State；不得重新导演或补全缺失创意。

## Production Identity
- Episode: EP002
- Scene: Scene02
- Shot: Shot02-01

## Output Format — Technical Lock
- Aspect Ratio: 9:16
- Orientation: PORTRAIT
- Target Canvas: 1080x1920

Generate a native vertical portrait composition on the locked canvas.
Do not output landscape. Do not letterbox or crop a landscape composition.
Recompose all reference assets naturally for the vertical frame; reference image
dimensions must never override this output format.
Camera Masters define camera position, direction, height and lens intent—not the
source canvas boundary. Environment Masters define spatial truth—not output ratio.

## Shot Execution
- Primary Function: INFORMATION_SHOT
- Primary Focus: 大漂亮从悲伤凝固到眼神恢复兴奋并喊出“燥起来！”
- Information Density: HIGH

## Camera / Coverage
- Camera Asset: cameras.entrance-hall-camera01
- Camera Status: MATCH
- Axis Status: PRESERVED
- Coverage: MEDIUM_WIDE
- Composition Intent: 入户门居后景中心并保持完全关闭；大漂亮位于门前主要动作区，小帅与阿诺分处前中景形成不均匀三角。静默时三猫都朝门，变脸后大漂亮成为唯一主动移动主体并走入画面较开阔的地面区域。

Camera Motion 只属于 VIDEO；静态 IMAGE 不得表现运镜后的结果。

## Character Visibility
- Visible: 大漂亮, 小帅, 阿诺
- Partial: None
- Off Screen: 小南

不得把 Off Screen 角色重新加入画面。

## Continuity
- Mode: CAMERA_CUT_CONTINUITY
- Previous Frame Policy: STATE_REFERENCE_ONLY
- Previous Frame Instruction: 只继承上一镜的 Identity / Space / Lighting / Props / Action State。不上传上一 Final；Camera / Coverage / Composition 以当前 Director Plan 为准。
- Locked Facts: Identity, Space, Lighting, Props, Action State
- Change Allowed: Coverage, Camera, Composition

## Start State
承接 Scene01 末镜：入户门刚完全关闭，小南已在门外；大漂亮、小帅和阿诺都留在室内地面，仍维持被识破后的短暂僵硬与朝门注意力。

## Frozen Moment — IMAGE 最高动作状态真相
关门后的安静刚开始，三只猫保持原位听门外动静，尚无任何一只猫解除离别表演。

### Physical Boundaries
- 入户门完全关闭，门扇与门框贴合，门把手静止
- 大漂亮四爪全部接触室内地面，身体仍朝向入户门，尚未走入空地
- 小帅四爪全部接触地面，身体停在玄关一侧，尚未转向室内通道
- 阿诺保持端坐，臀部和两只前爪稳定接触地面，胸腹尚未趴下
- 小南不在室内画面中，门内侧没有人体或手臂

### Forbidden Advanced States
- 大漂亮已经露出兴奋表情、喊出“燥起来”或开始跳舞
- 小帅已经冲向厨房或说出冻干台词
- 阿诺已经趴下或伸懒腰
- 门锁已经响起、入户门重新打开或小南探头回来
- 三只猫已经被折返的小南吓停

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
- Scene: Scene02
- Shot: Shot02-01

## Output Format — Technical Lock
- Aspect Ratio: 9:16
- Orientation: PORTRAIT
- Target Canvas: 1080x1920

The video must remain native vertical portrait throughout.
Do not output landscape, letterboxing or pillarboxing.

## Shot Delta
### Primary Action
安静持续数秒，三猫用耳位和目光确认门外无动静；大漂亮的悲伤眼神随即消失，恢复兴奋，喊“燥起来！”，并以真实四足步态走向门前空地。

### Secondary Actions
- 小帅仅以耳朵和视线跟随大漂亮，身体暂时留在原位
- 阿诺保持端坐，以克制眼神确认小南确实离开

### Performance Notes
前半段保持真实安静，不做夸张抖动；大漂亮的转变要快但集中在眼神、耳位和步态活力，喊话带少女式兴奋，不以拟人站立表现。

### Timing
- 0.0-1.8秒：门内安静，三猫听门外动静
- 1.8-2.5秒：大漂亮眼神和耳位从悲伤转为兴奋
- 2.5-4.5秒：大漂亮喊“燥起来！”并走向空地

## Camera Motion
- Movement: LOCKED_OFF
- Movement Reason: 固定画面可让数秒安静与突然变脸发生在同一空间基准内，反差由表演完成；移动镜头会提前暗示变化并削弱观察式笑点。

不得增加 Shot State 中不存在的额外运镜。

## End State
门仍完全关闭；大漂亮已到达开阔地面并以四足姿态准备起舞，小帅仍在一侧但注意力开始转向室内，阿诺仍端坐。

## Duration
- Estimated Duration: 4.5 seconds

## Continuity Lock
- Mode: CAMERA_CUT_CONTINUITY
- Locked Facts: Identity, Space, Lighting, Props, Action State
- Change Allowed: Coverage, Camera, Composition
- 只执行当前 Shot Delta，不得继续表演下一 Shot。
