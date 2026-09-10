# Shot Prompt Package

# ChatGPT Shot Handoff — Scene02 Shot02-02

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
- Shot: Shot02-02

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
- Primary Function: PERFORMANCE_SHOT
- Primary Focus: 大漂亮在空地上投入地跳短视频舞蹈
- Information Density: MEDIUM

## Camera / Coverage
- Camera Asset: cameras.entrance-hall-camera03
- Camera Status: MATCH
- Axis Status: PRESERVED
- Coverage: MEDIUM
- Composition Intent: 大漂亮位于门前空地中央偏下，完整猫身占据主要画面；关闭的入户门和木质门框保留为后景空间锚点，地面留出左右动作余量，小帅、阿诺和小南全部退出画面。

Camera Motion 只属于 VIDEO；静态 IMAGE 不得表现运镜后的结果。

## Character Visibility
- Visible: 大漂亮
- Partial: None
- Off Screen: 小帅, 阿诺, 小南

不得把 Off Screen 角色重新加入画面。

## Continuity
- Mode: CAMERA_CUT_CONTINUITY
- Previous Frame Policy: STATE_REFERENCE_ONLY
- Previous Frame Instruction: 只继承上一镜的 Identity / Space / Lighting / Props / Action State。不上传上一 Final；Camera / Coverage / Composition 以当前 Director Plan 为准。
- Locked Facts: Identity, Space, Lighting, Props, Action State
- Change Allowed: Coverage, Camera, Composition

## Start State
大漂亮已从三猫群像中走到门前空地，四爪落地并充满兴奋；小帅、阿诺仍在玄关其他位置，小南仍在门外，入户门关闭。

## Frozen Moment — IMAGE 最高动作状态真相
大漂亮刚站定在舞蹈区域、身体蓄势但尚未做出第一个舞步的最后稳定瞬间。

### Physical Boundaries
- 大漂亮四爪全部接触地面，躯干保持水平，没有以后肢直立
- 大漂亮与关闭的入户门之间保持可见地面距离，没有触碰门扇
- 画面左右均留有可见的舞步活动空间，大漂亮尚未跨出当前位置
- 入户门完全关闭，画面内没有小南身体部分
- 小帅和阿诺不进入当前构图

### Forbidden Advanced States
- 大漂亮已经抬爪、侧步、旋转或形成舞蹈中段姿势
- 大漂亮以人类方式双足站立或长时间腾空
- 小帅已经冲过画面或冻干已经出现
- 阿诺已经进入画面趴下
- 门锁已经响起、门已打开或小南已经返回

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
- Shot: Shot02-02

## Output Format — Technical Lock
- Aspect Ratio: 9:16
- Orientation: PORTRAIT
- Target Canvas: 1080x1920

The video must remain native vertical portrait throughout.
Do not output landscape, letterboxing or pillarboxing.

## Shot Delta
### Primary Action
大漂亮以真实猫体可完成的短视频舞蹈节奏连续表演：轻快侧步、交替短暂抬起前爪、头部和肩背配合节拍、尾巴随节奏摆动。

### Secondary Actions
- 兴奋目光保持投入，不再回看入户门
- 每个动作后至少三点稳定承重，不出现持续双足直立

### Performance Notes
投入程度要与刚才的悲伤形成强反差，但动作仍是猫咪身体可执行的游戏式律动；避免人类舞者手势、服装变化、夸张旋转和卡通残影。

### Timing
- 0.0-0.5秒：从蓄势进入第一拍
- 0.5-3.4秒：连续完成两到三个清楚可读的舞蹈节拍
- 3.4-4.2秒：停在仍有动势、可被后续门锁打断的舞姿

## Camera Motion
- Movement: LOCKED_OFF
- Movement Reason: 固定低机位让舞蹈节奏在稳定框架内自行制造活力，也便于保持四肢落点和猫体比例；跟拍或摇移会增加生成漂移并把轻喜剧处理得过度炫技。

不得增加 Shot State 中不存在的额外运镜。

## End State
大漂亮仍在门前空地投入跳舞，停留于一个真实猫体可保持的动态舞姿；门关闭，小帅和阿诺的状态在画外继续。

## Duration
- Estimated Duration: 4.2 seconds

## Continuity Lock
- Mode: CAMERA_CUT_CONTINUITY
- Locked Facts: Identity, Space, Lighting, Props, Action State
- Change Allowed: Coverage, Camera, Composition
- 只执行当前 Shot Delta，不得继续表演下一 Shot。
