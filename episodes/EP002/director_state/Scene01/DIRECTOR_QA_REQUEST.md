# EP002 Scene01 — Director QA Request

你现在只执行 Director QA，不重新导演，不生成图片，不生成 IMAGE PROMPT / VIDEO PROMPT。

审核对象是已经完成 Planning Import 的完整 Scene。

## 当前 Shot Plan

- Shot01-01: INFORMATION_SHOT / MEDIUM_WIDE / cameras.entrance-hall-camera01 / LOCKED_OFF
- Shot01-02: PERFORMANCE_SHOT / MEDIUM_CLOSE / cameras.entrance-hall-camera02 / LOCKED_OFF
- Shot01-03: PERFORMANCE_SHOT / MEDIUM / cameras.entrance-hall-camera03 / LOCKED_OFF
- Shot01-04: CHARACTER_REVEAL / MEDIUM_WIDE / cameras.entrance-hall-camera01 / LOCKED_OFF
- Shot01-05: EMOTIONAL_SHOT / MEDIUM_CLOSE / cameras.entrance-hall-camera02 / LOCKED_OFF
- Shot01-06: COMEDY_TIMING_SHOT / MEDIUM_WIDE / cameras.entrance-hall-camera01 / LOCKED_OFF

## 完整 Scene Director Plan（审核唯一对象）

```json
{
  "schema_version": "4.1",
  "episode_id": "EP002",
  "scene_id": "Scene01",
  "revision": 2,
  "plan_status": "LOCKED",
  "scene_director_decision": {
    "scene_goal": "用三只猫在小南出门前突然集体进入夸张离别表演、又被“只是取快递”当场拆穿的反差，建立本集轻喜剧开场并清晰展示四个角色的家庭关系。",
    "narrative_change": "三只猫从各自玩耍转为争相表达舍不得，小南短暂感动后揭示离开只是为了取快递，三只猫的悲情表演立刻失去支点；小南完成叮嘱并关门离开，为 Scene02 的真实状态反转建立直接起点。",
    "primary_character": "小南",
    "secondary_characters": [
      "大漂亮",
      "小帅",
      "阿诺"
    ],
    "audience_start_state": "观众只知道小南准备出门，尚不清楚三只猫会如何反应。",
    "audience_end_state": "观众看清三只猫各自不同的离别演技，并知道小南只是短暂取快递；期待门关后它们是否立刻变脸。",
    "emotion_curve": [
      "日常观察",
      "突然投入",
      "假性悲情升级",
      "短暂温情",
      "真相拆穿后的尴尬",
      "克制的喜剧悬停"
    ],
    "information_curve": [
      "小南准备出门，三只猫发现离开信号",
      "大漂亮最先采取行动并把普通离家解释成重大风险",
      "小帅迅速加码，把短暂分别演成永久失去",
      "阿诺以大家长姿态正式承诺照顾同伴",
      "小南揭示自己只是去取快递",
      "三只猫僵住并收回表演，小南关门离开"
    ],
    "rhythm_strategy": "先用短促群像动作完成钩子，再以大漂亮、小帅、阿诺三个递进式角色 Beat 逐层加码；小南的短暂停顿制造一秒真情，再用生活化真相击穿宏大情绪，最后保留集体僵住的静默拍点并迅速完成离场。",
    "primary_style": "生活观察式反差喜剧（导演风格排序第1）",
    "secondary_style": "克制型家庭情感喜剧（导演风格排序第2）",
    "scene_visual_strategy": "视觉注意力从玄关群像依次收束到大漂亮怀中表演、小帅腿边表演，再回到阿诺与完整群体；小南揭示真相时降低信息密度，让语言与轻触成为中心，随后回到宽一些的群像承接三猫同步僵住和门的关闭。",
    "scene_camera_strategy": "以 Entrance Hall Camera01 建立并反复校正玄关轴线、人物站位和门的位置；单猫表演需要分别切到人猫怀中互动中近景与脚边低机位中景，均保持门—小南—猫的同一空间方向；笑点揭示后回到 Camera01 的稳定群像，所有镜头原则上锁定机位，让表演停顿而非运镜承担喜剧节奏。",
    "scene_end_intent": "让门在三只猫面前完全关闭，把尴尬静止状态留在屋内，并为 Scene02“门关闭后安静几秒再瞬间恢复本性”提供无歧义的连续起点。"
  },
  "scene_assets": {
    "environment_asset": "environments.玄关master2",
    "character_assets": {
      "小南": "characters.小南-xiaonan-master",
      "大漂亮": "characters.大漂亮-dapiaoliang-master",
      "小帅": "characters.小帅-xiaoshuai-master",
      "阿诺": "characters.阿诺-arno-master"
    },
    "outfit_assets": {
      "小南": "outfits.小南_周末休闲外出款"
    },
    "prop_assets": []
  },
  "shots": [
    {
      "shot_id": "Shot01-01",
      "order": 1,
      "primary_function": "INFORMATION_SHOT",
      "secondary_effect": "COMEDY_SETUP",
      "narrative_purpose": "建立玄关空间、小南即将出门及三只猫原本分散的状态，并用三猫同步捕捉离开信号与大漂亮率先冲入怀中的动作形成开场钩子。",
      "audience_feeling": "从普通日常迅速进入好奇和轻微好笑。",
      "information_gain": "观众确认四个角色的位置关系，并看到大漂亮是第一个把离家信号转化为行动的猫。",
      "why_this_shot": "Scene 首镜必须先让观众看清门、小南和三只猫的完整地理关系，随后在同一空间中读取气氛突变和大漂亮的率先行动。",
      "why_not_previous_shot": "这是 Scene 首镜，没有上一镜可承担空间建立与开场钩子；Scene 开始前也不存在可继承的已锁定画面。",
      "primary_focus": "小南准备出门与三只猫同时改变注意力",
      "secondary_focus": "大漂亮率先冲向小南并被接入怀中",
      "coverage": "MEDIUM_WIDE",
      "coverage_reason": "中大全景足以同时呈现入户门、换鞋区、小南全身和三只猫分散位置，并让大漂亮从地面到怀中的完整运动路径保持可读。",
      "composition_intent": "入户门作为后景中心和离开信号，小南位于门前主要纵轴；三只猫在前中景形成不均匀三角分布，大漂亮离小南最近，小帅稍后，阿诺最稳；大漂亮启动后成为画面内唯一快速移动主体，其余角色保持清楚但不争抢注意力。",
      "information_density": "HIGH",
      "visible_characters": [
        "小南",
        "大漂亮",
        "小帅",
        "阿诺"
      ],
      "partial_characters": [],
      "off_screen_characters": [],
      "camera_requirement": {
        "purpose": "建立玄关地理并覆盖大漂亮从地面冲向小南、被小南接住的完整路径",
        "scale": "MEDIUM_WIDE",
        "subject_zone": "入户门前换鞋区及其向室内延伸的猫咪活动地面",
        "axis_requirement": "建立从室内低位观察入户门的玄关主轴，后续镜头不得越过小南与三猫形成的互动轴",
        "lens_intent": "保留空间纵深和四个角色的尺寸差，同时避免低机位广角夸张变形"
      },
      "selected_camera": "cameras.entrance-hall-camera01",
      "camera_status": "MATCH",
      "camera_reason": "Camera01 已登记并直接面对入户门，能够完整呈现门前地面、换鞋区和大漂亮的运动路径，是当前资产中承担空间建立的明确匹配机位。",
      "camera_motion": "LOCKED_OFF",
      "camera_motion_reason": "开场需要先锁定空间并让三猫同步变脸与大漂亮的冲刺在稳定画面内形成反差，移动摄影会削弱位置认知和喜剧突变。",
      "axis_status": "NEW_AXIS_ESTABLISHED",
      "continuity_mode": "CAMERA_CUT_CONTINUITY",
      "previous_frame_policy": "NONE",
      "start_state": {
        "description": "下午的玄关，入户门关闭；小南已穿周末休闲外出款并站在门前准备离开，三只猫在室内地面各自处于自然玩耍或休息后的稳定位置，尚未进入离别表演。"
      },
      "frozen_moment": {
        "description": "三只猫刚刚发现小南准备离开的最后一个稳定瞬间，注意力已转向小南但集体表演尚未启动。",
        "physical_boundaries": [
          "入户门完全关闭，门扇与门框贴合，门把手未被小南按下",
          "小南双脚都在室内地面，身体朝向门，双手尚未抱猫",
          "大漂亮四爪全部接触地面，与小南身体之间仍有清楚可见的空隙",
          "小帅四爪全部接触地面，前爪尚未触碰小南腿部",
          "阿诺身体保持在原地，尚未走到小南正前方坐下"
        ],
        "forbidden_advanced_states": [
          "大漂亮已经离地、被抱起或进入小南怀中",
          "小帅已经抱住小南的腿",
          "阿诺已经端正坐在小南面前",
          "小南已经打开入户门或跨出门外",
          "任一角色已经开始说出台词"
        ]
      },
      "shot_delta": {
        "primary_action": "三只猫的视线几乎同时锁定小南，身体状态从松散迅速变得专注；大漂亮第一个冲到小南脚边并真实起跳，小南顺势弯身接住它，让它稳定进入怀中。",
        "secondary_actions": [
          "小帅从原位置靠近一步但仍未抱腿，为下一镜保留动作起点",
          "阿诺抬头观察并缓慢起身，但尚未走到小南正前方"
        ],
        "performance_notes": "变化要像猫咪捕捉到熟悉离家信号后的自然集体反应；大漂亮投入最快，但动作仍是写实猫咪起跳，不使用拟人站立或动画式夸张。",
        "timing": [
          "0.0-0.8秒：小南整理离开状态，三猫保持分散",
          "0.8-1.5秒：三猫同时抬眼并锁定小南，留半拍气氛突变",
          "1.5-3.8秒：大漂亮冲近、起跳，小南弯身接住并恢复稳定站姿"
        ]
      },
      "end_state": {
        "description": "大漂亮被小南稳定抱在怀中并正面关注她；小帅已靠近小南腿边但双前爪仍在地面；阿诺已起身，仍在稍后方；入户门保持关闭。"
      },
      "estimated_duration": 3.8,
      "scene_end": false,
      "next_shot": "Shot01-02"
    },
    {
      "shot_id": "Shot01-02",
      "order": 2,
      "primary_function": "PERFORMANCE_SHOT",
      "secondary_effect": "CHARACTER_REVEAL",
      "narrative_purpose": "让大漂亮以认真担忧的怀中表演完成第一层离别演技，建立她情绪投入最快、最主动的角色差异。",
      "audience_feeling": "明知夸张却短暂被它的认真感染。",
      "information_gain": "大漂亮把普通出门解释为“外面的世界竞争太激烈”，离别演技由动作升级为完整情绪表达。",
      "why_this_shot": "大漂亮的蓝眼、耳位、抬头视线与小南抱持关系是本 Beat 的信息主体，需要从群像中独立出来才能让台词的认真感和反差成立。",
      "why_not_previous_shot": "Camera01 的中大全景已经完成空间与起跳动作，但无法清楚读取怀中猫咪的细微担忧表演；继续留在上一镜会让长台词落在过小主体上并稀释角色揭示。",
      "primary_focus": "大漂亮在小南怀中的认真担忧表演",
      "secondary_focus": "小南被突如其来郑重告别弄愣的轻微反应",
      "coverage": "MEDIUM_CLOSE",
      "coverage_reason": "中近景可同时保留大漂亮完整头胸、前爪与小南抱持它的双臂及部分面部反应，让猫的表演和人猫关系同等清晰，而不塞入其余角色。",
      "composition_intent": "大漂亮占画面主要视觉面积并位于小南怀中上扬视线，小南的下半张脸、眼神和双臂作为关系框架进入画面；入户门或木质门框以柔焦背景维持玄关身份，小帅与阿诺完全退出画面。",
      "information_density": "LOW",
      "visible_characters": [
        "大漂亮"
      ],
      "partial_characters": [
        "小南"
      ],
      "off_screen_characters": [
        "小帅",
        "阿诺"
      ],
      "camera_requirement": {
        "purpose": "读取怀中单猫的认真担忧表情与小南被打动前的细小反应",
        "scale": "MEDIUM_CLOSE",
        "subject_zone": "入户门前小南上半身与怀中猫咪区域",
        "axis_requirement": "保持 Camera01 已建立的室内朝门方向及大漂亮仰视小南的视线关系，不从门外反拍",
        "lens_intent": "适度压缩背景并突出猫眼、耳位和抱持关系，保持自然面部与毛发比例"
      },
      "selected_camera": "cameras.entrance-hall-camera02",
      "camera_status": "MATCH",
      "camera_reason": "Entrance Hall Camera02 保持 Camera01 已建立的室内朝门方向，并以更紧凑的竖向中近景覆盖入户门前上半身互动区域；小南面部、抱持双臂和怀中大漂亮可共同进入主要画面，木质门与门框能够作为稳定的玄关背景，同时排除脚边小帅和地面阿诺，符合本镜的表演读取、构图和轴线要求。",
      "camera_motion": "LOCKED_OFF",
      "camera_motion_reason": "台词的笑点来自大漂亮过度认真的静态凝视与小南半拍发愣，锁定画面比推近更能保留克制观察感。",
      "axis_status": "PRESERVED",
      "continuity_mode": "CAMERA_CUT_CONTINUITY",
      "previous_frame_policy": "STATE_REFERENCE_ONLY",
      "start_state": {
        "description": "承接 Shot01-01：大漂亮已经稳定处于小南怀中，身体得到双臂支撑；小南仍站在关闭的入户门内；小帅和阿诺保持上一镜结束位置但在本镜画外。"
      },
      "frozen_moment": {
        "description": "大漂亮在小南怀中稳定下来、即将开口说“主人……”之前的静止凝视。",
        "physical_boundaries": [
          "大漂亮胸腹由小南双臂稳定支撑，身体没有继续上升或下落",
          "大漂亮前爪自然搭在小南手臂附近，没有挥爪或触碰小南面部",
          "大漂亮嘴部闭合，视线向上落在小南脸部",
          "小南双脚仍在门内地面，抱持姿势稳定，身体没有朝门外移动",
          "入户门完全关闭"
        ],
        "forbidden_advanced_states": [
          "大漂亮已经开始或已经说完离别台词",
          "小南已经笑出声或开始回答",
          "小帅已经抱住小南腿部并进入本镜画面",
          "阿诺已经坐到小南正前方",
          "入户门已经打开"
        ]
      },
      "shot_delta": {
        "primary_action": "大漂亮保持被抱住的真实猫咪姿态，认真仰视小南并说：“主人……外面的世界竞争太激烈了。你一定要注意安全。”",
        "secondary_actions": [
          "小南先轻微睁大眼并停顿，没有立刻回应",
          "大漂亮在句尾维持担忧凝视，不追加夸张肢体动作"
        ],
        "performance_notes": "大漂亮的情绪投入必须真诚而非故意搞怪；以眼神、耳位和稳定姿态表演，不做拟人式手势。小南只给克制的意外反应。",
        "timing": [
          "0.0-0.6秒：怀中静止凝视",
          "0.6-5.1秒：大漂亮自然完成两句台词",
          "5.1-5.8秒：保留小南发愣与大漂亮认真等待的半拍"
        ]
      },
      "end_state": {
        "description": "大漂亮仍被小南稳稳抱住并保持担忧目光；小南由意外进入短暂迟疑，尚未回答；门仍关闭，小帅即将从画外抱腿。"
      },
      "estimated_duration": 5.8,
      "scene_end": false,
      "next_shot": "Shot01-03"
    },
    {
      "shot_id": "Shot01-03",
      "order": 3,
      "primary_function": "PERFORMANCE_SHOT",
      "secondary_effect": "COMEDY_ESCALATION",
      "narrative_purpose": "让小帅用抱腿和颤抖语气把大漂亮的安全提醒升级成“可能永远回不来”，完成第二层更夸张的离别演技。",
      "audience_feeling": "从轻微共情转为明确识别这是一场过度表演。",
      "information_gain": "小帅不仅跟进，还主动把风险推到最极端，显示他嘴快、自信加码的角色特征。",
      "why_this_shot": "小帅的动作发生在小南腿边，视觉高度与上一镜怀中大漂亮完全不同；单独低位呈现能让前爪接触、仰视和颤抖语气成为清楚的升级动作。",
      "why_not_previous_shot": "上一镜的中近景视觉中心在小南怀中，腿边区域不在有效覆盖内；强行兼顾小帅会破坏大漂亮的低信息密度表演，也无法清楚验证抱腿动作。",
      "primary_focus": "小帅靠近并抱住小南腿部的悲情加码",
      "secondary_focus": "小南腿部保持稳定以及怀中大漂亮在画外继续被抱持的连续状态",
      "coverage": "MEDIUM",
      "coverage_reason": "低机位中景可以完整显示小帅身体、前爪与小南小腿之间的真实接触，并保留足够地面空间说明它不是拟人站立。",
      "composition_intent": "小帅位于画面下半部主焦点，后爪和身体重量明确落在地面，双前爪短暂贴住小南一侧小腿；小南只以膝下腿部进入画面形成尺度和依附关系，背景保留门口地垫或鞋柜边缘作为空间锚点。",
      "information_density": "LOW",
      "visible_characters": [
        "小帅"
      ],
      "partial_characters": [
        "小南"
      ],
      "off_screen_characters": [
        "大漂亮",
        "阿诺"
      ],
      "camera_requirement": {
        "purpose": "清楚验证小帅从四爪着地到前爪抱腿的真实猫咪动作，并读取仰视表演",
        "scale": "MEDIUM",
        "subject_zone": "小南脚边及门前猫咪活动地面",
        "axis_requirement": "保持 Camera01 的门内主轴和小帅朝向小南的屏幕方向，不绕到小南腿部另一侧反打",
        "lens_intent": "自然呈现猫体和人腿比例，避免超广角把猫头、爪或小南腿部夸张变形"
      },
      "selected_camera": "cameras.entrance-hall-camera03",
      "camera_status": "MATCH",
      "camera_reason": "Entrance Hall Camera03 从门内同侧轴线以贴近地面的低机位观察小南脚边活动区，前景保留充足地面，可完整容纳小帅身体、着地后爪、抬起前爪与小南一侧小腿的接触关系；入户门、地垫和鞋柜仍提供明确空间锚点，能够在不越轴和不过度广角变形的条件下完成真实抱腿动作验证。",
      "camera_motion": "LOCKED_OFF",
      "camera_motion_reason": "抱腿动作和颤抖台词本身承担升级，固定低机位可让真实接触边界清晰，避免跟拍造成拟人站立或爪部错位。",
      "axis_status": "PRESERVED",
      "continuity_mode": "CAMERA_CUT_CONTINUITY",
      "previous_frame_policy": "STATE_REFERENCE_ONLY",
      "start_state": {
        "description": "承接 Shot01-02：大漂亮仍在小南怀中；小南站在关闭的门内尚未回答；小帅已在小南腿边，四爪着地并仰头，尚未抬起前爪；阿诺在稍后方缓慢靠近。"
      },
      "frozen_moment": {
        "description": "小帅已来到小南腿边、即将抬起前爪抱腿前的稳定四爪着地状态。",
        "physical_boundaries": [
          "小帅四只爪全部接触门内地面，后腿承重清楚",
          "小帅胸腹没有贴住小南腿部，身体与小南小腿之间仍有窄小可见空隙",
          "小帅两只前爪尚未离地或搭上小南腿部",
          "小南双脚位置不变，裙摆与腿部保持自然垂落",
          "入户门保持完全关闭"
        ],
        "forbidden_advanced_states": [
          "小帅已经双足直立或以人类姿势站立",
          "小帅已经抱住腿并说完台词",
          "小南已经弯腰安慰小帅或开始回答",
          "大漂亮已经从小南怀中下来",
          "阿诺已经坐到小南正前方"
        ]
      },
      "shot_delta": {
        "primary_action": "小帅保持后腿和身体重量贴近地面，短暂抬起前爪抱住小南一侧小腿，仰头用颤抖语气说：“主人……如果你回不来了……我们该怎么办呀？”",
        "secondary_actions": [
          "说到“回不来了”时停半拍后再完成后半句",
          "小南腿部保持不动，不通过夸张踉跄放大动作"
        ],
        "performance_notes": "小帅是在自信地升级悲情，不是失去常识；动作必须保持真实猫咪短暂扒腿姿态，禁止长时间双足直立和人类式搂抱。",
        "timing": [
          "0.0-0.7秒：小帅四爪着地仰视",
          "0.7-1.5秒：前爪贴上小南小腿并稳定身体",
          "1.5-5.8秒：完成台词，中间在第二个省略号处留自然停顿",
          "5.8-6.5秒：维持悲伤表情等待回应"
        ]
      },
      "end_state": {
        "description": "小帅前爪仍贴在小南一侧小腿，后腿承重并仰头保持悲伤表情；大漂亮仍在小南怀中；阿诺已靠近到小南正前方附近但尚未坐下；门仍关闭。"
      },
      "estimated_duration": 6.5,
      "scene_end": false,
      "next_shot": "Shot01-04"
    },
    {
      "shot_id": "Shot01-04",
      "order": 4,
      "primary_function": "CHARACTER_REVEAL",
      "secondary_effect": "COMEDY_ESCALATION",
      "narrative_purpose": "让阿诺以端正坐姿和正式承诺完成三猫离别演技的最高点，同时重新建立完整群体关系，让小南的短暂感动有可见对象。",
      "audience_feeling": "感到一本正经的荒诞，同时接受三只猫确实关心小南。",
      "information_gain": "阿诺自然承担大家长角色，三只猫形成完整的情绪与行动层级，小南也被这套集体表演短暂打动。",
      "why_this_shot": "阿诺的喜剧价值来自他与怀中大漂亮、腿边小帅组成的完整家庭构图，必须回到空间关系清楚的群像才能读出“照顾他们两个”的指代和一本正经反差。",
      "why_not_previous_shot": "上一镜只覆盖脚边小帅，阿诺和怀中大漂亮均在画外，无法建立承诺对象、三猫层级与小南对整体的反应；继续低位单猫覆盖会丢失台词关系。",
      "primary_focus": "阿诺走到小南正前方端正坐下并郑重承诺",
      "secondary_focus": "大漂亮与小帅维持悲伤表演，小南由意外转为短暂感动",
      "coverage": "MEDIUM_WIDE",
      "coverage_reason": "中大全景能够同时容纳小南、怀中大漂亮、腿边小帅和正前方阿诺，并保留门与换鞋区以维持人物指向和场景地理。",
      "composition_intent": "小南在门前形成竖向中心，怀中大漂亮位于上层、腿边小帅位于下层、阿诺在前方地面端正居中，三猫形成围绕小南的层级三角；门保持后景中心，观众第一眼落在阿诺严肃坐姿，随后读到另外两猫的悲伤配合和小南软化的表情。",
      "information_density": "HIGH",
      "visible_characters": [
        "小南",
        "大漂亮",
        "小帅",
        "阿诺"
      ],
      "partial_characters": [],
      "off_screen_characters": [],
      "camera_requirement": {
        "purpose": "重建完整群体关系并让阿诺的正式承诺与“他们两个”的指向同时可见",
        "scale": "MEDIUM_WIDE",
        "subject_zone": "入户门前小南站位、怀中区域和脚边三猫活动区",
        "axis_requirement": "回到 Shot01-01 建立的室内朝门主轴，不越过群体互动轴",
        "lens_intent": "保持空间纵深和四角色层级，避免压扁阿诺与小南之间的距离"
      },
      "selected_camera": "cameras.entrance-hall-camera01",
      "camera_status": "MATCH",
      "camera_reason": "Camera01 的门内正向低位中大全景正好恢复完整玄关群体关系，并与首镜共享明确轴线和空间比例。",
      "camera_motion": "LOCKED_OFF",
      "camera_motion_reason": "阿诺的笑点依赖端正坐下后像正式负责人一样稳定发言，固定镜头让其严肃姿态与另外两猫的夸张悲伤形成可观察反差。",
      "axis_status": "PRESERVED",
      "continuity_mode": "CAMERA_CUT_CONTINUITY",
      "previous_frame_policy": "STATE_REFERENCE_ONLY",
      "start_state": {
        "description": "承接 Shot01-03：小南仍在门内抱着大漂亮，小帅前爪贴在小南一侧小腿，阿诺已走到小南正前方附近但仍四爪站立，入户门关闭。"
      },
      "frozen_moment": {
        "description": "阿诺已经走到小南正前方、即将收腿端正坐下之前的稳定站立瞬间。",
        "physical_boundaries": [
          "阿诺四爪全部接触地面，臀部尚未落地，前腿仍为站立承重状态",
          "阿诺与小南之间保留一只猫身长度以内的清楚地面间距",
          "大漂亮仍由小南双臂支撑在怀中，没有下地",
          "小帅前爪仍贴在小南小腿，后腿与腹部靠近地面承重",
          "入户门保持完全关闭"
        ],
        "forbidden_advanced_states": [
          "阿诺已经端正坐好或已经说出承诺",
          "小南已经笑出来或揭示取快递",
          "大漂亮已经从怀中下来",
          "小帅已经松开前爪",
          "入户门已经打开"
        ]
      },
      "shot_delta": {
        "primary_action": "阿诺缓慢收腿，在小南正前方端正坐好，抬头以严肃稳定的语气说：“主人放心。我会照顾好他们两个。”",
        "secondary_actions": [
          "大漂亮和小帅继续维持悲伤表情，不新增动作抢戏",
          "小南依次看过三只猫，表情由错愕轻微软化，短暂被感动但尚未笑"
        ],
        "performance_notes": "阿诺完全相信自己正在做可靠承诺，语气不得带自知搞笑；小南的感动只持续一拍，为下一镜的生活化拆穿保留反差。",
        "timing": [
          "0.0-1.2秒：阿诺缓慢坐正并抬头",
          "1.2-4.8秒：阿诺完成两句承诺",
          "4.8-6.5秒：小南看过三猫并短暂感动，保留静默拍点"
        ]
      },
      "end_state": {
        "description": "阿诺在小南正前方端正坐好并保持严肃目光；大漂亮仍在怀中，小帅仍抱腿；小南看着三只猫短暂动容，尚未笑或说明真相；门保持关闭。"
      },
      "estimated_duration": 6.5,
      "scene_end": false,
      "next_shot": "Shot01-05"
    },
    {
      "shot_id": "Shot01-05",
      "order": 5,
      "primary_function": "EMOTIONAL_SHOT",
      "secondary_effect": "COMEDY_TURN",
      "narrative_purpose": "让小南从短暂感动转为忍笑，以摸头回应三猫的心意，再用“只是出去取个快递”完成生活化真相揭示。",
      "audience_feeling": "先感到温柔，随即因巨大情绪落差发笑。",
      "information_gain": "观众得到 Scene 的关键真相：小南不会远行，只是短暂取快递，三只猫此前的悲情规模完全过度。",
      "why_this_shot": "真相需要落在小南的细微表情变化、摸头动作和大漂亮的近距离接收反应上，才能同时保留家庭温度与反差，而不是把揭示处理成宽景中的信息播报。",
      "why_not_previous_shot": "上一镜必须容纳四个角色以完成阿诺的群体承诺，信息密度过高，无法精确读取小南从感动一秒到忍不住笑的渐变，也会削弱摸头与真相台词的亲密感。",
      "primary_focus": "小南从动容到忍笑并温柔揭示只是取快递",
      "secondary_focus": "大漂亮在怀中接受摸头并保持尚未消化真相的凝视",
      "coverage": "MEDIUM_CLOSE",
      "coverage_reason": "中近景可覆盖小南面部、上身、抱持双臂和大漂亮头部，让情绪渐变、摸头接触与两句台词同时可读，并主动排除脚边复杂动作。",
      "composition_intent": "小南面部与大漂亮头部形成上下双焦点，小南一只手从抱持位置移到大漂亮头顶；门的木质色块柔焦留在背景，脚边小帅和地面阿诺均不进入画面，视线重点保持在小南的克制笑意。",
      "information_density": "LOW",
      "visible_characters": [
        "小南",
        "大漂亮"
      ],
      "partial_characters": [],
      "off_screen_characters": [
        "小帅",
        "阿诺"
      ],
      "camera_requirement": {
        "purpose": "读取小南情绪渐变、摸头接触与怀中大漂亮的近距离反应",
        "scale": "MEDIUM_CLOSE",
        "subject_zone": "入户门前小南上半身与怀中猫咪区域",
        "axis_requirement": "沿用 Shot01-02 所需的室内朝门互动轴，不从大漂亮视线反侧越轴",
        "lens_intent": "自然压缩背景并保留人脸、手和猫头的真实比例，重点分离眼神与触摸"
      },
      "selected_camera": "cameras.entrance-hall-camera02",
      "camera_status": "MATCH",
      "camera_reason": "复用 Entrance Hall Camera02 可与 Shot01-02 建立明确的视觉回环，并保持相同的室内朝门互动轴、人物尺度和玄关背景关系；其紧凑竖向画面能够同时读取小南由动容转为忍笑的面部变化、手部摸头动作和怀中大漂亮的反应，同时自然排除脚边角色，符合本镜中近景揭示笑点的构图与连续性要求。",
      "camera_motion": "LOCKED_OFF",
      "camera_motion_reason": "小南先动容、再忍笑、最后平静揭示的表演需要稳定观察，额外推近会把生活化反差处理得过度煽情。",
      "axis_status": "PRESERVED",
      "continuity_mode": "CAMERA_CUT_CONTINUITY",
      "previous_frame_policy": "STATE_REFERENCE_ONLY",
      "start_state": {
        "description": "承接 Shot01-04：小南仍站在关闭的门内抱着大漂亮，表情刚刚软化；小帅在腿边抱住一侧小腿，阿诺正前方端坐但在本镜画外。"
      },
      "frozen_moment": {
        "description": "小南被三猫打动一秒、笑意尚未明显出现且手尚未开始摸大漂亮头部的稳定瞬间。",
        "physical_boundaries": [
          "大漂亮仍由小南一侧手臂和身体稳定支撑，身体没有下落",
          "小南准备摸头的手仍停在大漂亮头顶之外，手掌与毛发之间有可见空隙",
          "小南嘴唇闭合，尚未说“你们三个……”",
          "大漂亮头部朝向小南，耳朵和眼神保持认真等待",
          "入户门保持完全关闭"
        ],
        "forbidden_advanced_states": [
          "小南已经明显大笑或已经说完取快递真相",
          "小南的手已经接触并完成摸头",
          "大漂亮已经从怀中下来",
          "小帅已经松开小南腿部",
          "阿诺已经改变端正坐姿",
          "入户门已经打开"
        ]
      },
      "shot_delta": {
        "primary_action": "小南的感动只维持一拍，随后忍不住轻轻笑出来，说：“你们三个……”；她温柔摸了摸大漂亮的头，再自然说明：“我只是出去取个快递。很快回来。”",
        "secondary_actions": [
          "大漂亮在被摸头时保持安静，听到“取个快递”后眼神停住但尚未下地",
          "画外的小帅和阿诺不发声，为真相落地留出静默"
        ],
        "performance_notes": "小南不是嘲笑三只猫，而是被关心后觉得它们演得太过；笑意温柔克制。真相台词保持生活口语，不做包袱式重音。",
        "timing": [
          "0.0-0.8秒：小南动容停顿",
          "0.8-2.2秒：忍笑并说“你们三个……”",
          "2.2-3.3秒：完成一次自然摸头",
          "3.3-6.3秒：说完“我只是出去取个快递。很快回来。”",
          "6.3-7.0秒：小南与大漂亮保持静止，让真相落地"
        ]
      },
      "end_state": {
        "description": "小南已经说明只是取快递并停止摸头，仍抱着大漂亮；大漂亮表情僵住，小帅仍抱腿但在画外停住，阿诺仍端坐且保持严肃；门依旧关闭。"
      },
      "estimated_duration": 7.0,
      "scene_end": false,
      "next_shot": "Shot01-06"
    },
    {
      "shot_id": "Shot01-06",
      "order": 6,
      "primary_function": "COMEDY_TIMING_SHOT",
      "secondary_effect": "SCENE_EXIT",
      "narrative_purpose": "用完整群像展示三猫被真相同时冻住、默默收回各自表演，再让小南叮嘱并关门离开，完成笑点 Payoff 和 Scene02 的连续性入口。",
      "audience_feeling": "在尴尬静默中发笑，并自然期待门后反转。",
      "information_gain": "三只猫的悲伤迅速失去支点：大漂亮下地、小帅松爪、阿诺只剩严肃坐姿；小南最终确实离开且门完全关闭。",
      "why_this_shot": "笑点必须由三只猫同一时刻的僵住和依次撤回动作共同完成，并且门的开启、人物离开与关闭需要可验证的空间全貌，宽一些的稳定群像是 Scene 收束所必需。",
      "why_not_previous_shot": "上一镜只聚焦小南与怀中大漂亮，无法同时看到小帅松爪、阿诺维持严肃、三猫集体尴尬以及门从关闭到再次关闭的完整结果；继续中近景会丢失 Payoff 和下一 Scene 的物理起点。",
      "primary_focus": "三只猫集体僵住后收回离别表演",
      "secondary_focus": "小南打开门、完成叮嘱并关门离开",
      "coverage": "MEDIUM_WIDE",
      "coverage_reason": "中大全景可以同时容纳四个角色、入户门和门内地面，让集体停顿、三个不同撤回动作及门的最终关闭都在同一稳定空间中可验证。",
      "composition_intent": "回到 Camera01 的门内正向构图：小南在门前，大漂亮仍在怀中起始，小帅位于腿边，阿诺在正前方端坐；先让三猫的僵硬层级占据注意力，随后小南与门的动作成为中心。门关闭后，三猫留在室内前中景，形成通向 Scene02 的最终画面。",
      "information_density": "HIGH",
      "visible_characters": [
        "小南",
        "大漂亮",
        "小帅",
        "阿诺"
      ],
      "partial_characters": [],
      "off_screen_characters": [],
      "camera_requirement": {
        "purpose": "完整呈现集体僵住、三猫撤回动作与入户门关闭的 Scene Payoff",
        "scale": "MEDIUM_WIDE",
        "subject_zone": "入户门、门前小南站位及室内三猫地面区域",
        "axis_requirement": "严格回到并保持 Camera01 建立的门内正向主轴，门开启期间也不越到门外",
        "lens_intent": "保持人物、猫和门的空间比例清楚，使门关闭成为明确可验证的最终事件"
      },
      "selected_camera": "cameras.entrance-hall-camera01",
      "camera_status": "MATCH",
      "camera_reason": "Camera01 同时覆盖门体、门前完整人物和三猫地面区域，且与 Scene 开场共享构图基准，最适合完成集体尴尬 Payoff 与门关闭的连续性校验。",
      "camera_motion": "LOCKED_OFF",
      "camera_motion_reason": "尴尬笑点依赖空气凝固和角色缓慢撤回，固定机位能把停顿留给观众；门的关闭也无需跟随即可清楚完成。",
      "axis_status": "PRESERVED",
      "continuity_mode": "CAMERA_CUT_CONTINUITY",
      "previous_frame_policy": "STATE_REFERENCE_ONLY",
      "start_state": {
        "description": "承接 Shot01-05 真相落地后的第一拍：小南仍在关闭的门内抱着大漂亮；大漂亮表情僵住；小帅前爪仍贴在小南小腿且停止表演；阿诺仍在正前方端正坐着并保持严肃。"
      },
      "frozen_moment": {
        "description": "“只是取个快递”真相落地后，三只猫同时僵住且尚未撤回任何表演动作的集体静止瞬间。",
        "physical_boundaries": [
          "大漂亮仍完整处于小南怀中，四爪尚未回到地面",
          "小帅前爪仍贴在小南一侧小腿，尚未松开，后腿仍在地面承重",
          "阿诺臀部与前爪稳定接触地面，保持端正坐姿",
          "小南双脚仍在门内，抱持大漂亮，手尚未移向门把手",
          "入户门完全关闭"
        ],
        "forbidden_advanced_states": [
          "大漂亮已经下地或转身离开",
          "小帅已经松开前爪或跑开",
          "阿诺已经起身或放松趴下",
          "小南已经打开门、说完叮嘱或走到门外",
          "入户门已经再次关闭且小南已在门外"
        ]
      },
      "shot_delta": {
        "primary_action": "保持一拍集体尴尬后，大漂亮慢慢从小南怀中回到地面，小帅松开前爪恢复四爪着地，阿诺仍维持严肃端坐；小南转向门、打开门，在跨出前回头说：“在家乖一点。”随后走出并从外侧把门完全关上。",
        "secondary_actions": [
          "三只猫在收回动作时互不对视，不用额外对白解释尴尬",
          "门打开时三只猫都留在门内，不跟随小南跨过门槛",
          "门关闭后保留三只猫在屋内面对门的稳定状态"
        ],
        "performance_notes": "先让静默足够落下笑点，再以慢半拍、尽量若无其事的撤回制造尴尬；阿诺不崩掉严肃姿态。小南的叮嘱自然宠溺，不强化胜负感。",
        "timing": [
          "0.0-1.2秒：三猫集体僵住，空气安静",
          "1.2-3.6秒：大漂亮下地，小帅松爪，阿诺保持端坐",
          "3.6-5.3秒：小南转身并打开门",
          "5.3-6.7秒：小南回头说“在家乖一点。”",
          "6.7-8.2秒：小南跨出并把门完全关上",
          "8.2-8.8秒：三猫留在门内，门关闭，保持短暂静止"
        ]
      },
      "end_state": {
        "description": "入户门已经从外侧完全关闭，小南位于门外且不再可见；大漂亮四爪着地靠近原抱持位置，小帅四爪着地靠近原腿边位置，阿诺仍在门前端正坐着；三只猫留在屋内面对关闭的门，Scene02 可从同一空间的安静状态直接开始。"
      },
      "estimated_duration": 8.8,
      "scene_end": true,
      "next_shot": "Scene02"
    }
  ],
  "scene_end_state": {
    "description": "Scene01 结束时入户门完全关闭，小南已经在门外且不可见；大漂亮、小帅、阿诺均留在玄关门内，大漂亮和小帅已撤回抱持动作，阿诺仍端正坐着。三猫刚经历离别演技被拆穿后的短暂尴尬，空间、光照、门状态与角色位置直接交给 Scene02 的“屋内安静几秒”。"
  },
  "next_scene": "Scene02"
}
```

## 必须审核

1. Narrative Coverage
   - Scene Goal 是否被完整覆盖
   - 是否存在剧情信息缺失
   - Scene End 是否成立

2. Shot Necessity
   - 每个 Shot 是否真的必要
   - why_this_shot 是否成立
   - why_not_previous_shot 是否成立
   - 是否存在仅因微小动作变化而拆出的 Shot

3. Visual Differentiation
   - 相邻 Shot 的 Coverage / Camera / Composition / Information Density 是否有叙事理由
   - 是否出现连续多个视觉近似镜头
   - 是否缺少必要的 Reaction / Insert / Establishing / Transition

4. Camera & Motion
   - Camera 是否服务叙事
   - Camera Motion 是否必要
   - 不得为了“有运镜”而运镜
   - NEED_NEW_CAMERA 时必须明确指出

5. Continuity
   - SAME_CAMERA_CONTINUATION 是否真的需要继承上一 Final Frame
   - CAMERA_CUT_CONTINUITY 是否错误地把上一 Final Frame 当成最高优先级
   - 切镜时 Identity / Space / Lighting / Props / Action State 是否可连续

6. Frozen Moment
   - Image Prompt 首帧状态是否早于动作发生
   - physical_boundaries 是否可见、可验证
   - forbidden_advanced_states 是否阻止“准备起跳却已经跳起”等问题

7. Rhythm
   - Scene 是否被过度切碎
   - 是否景别单一
   - 是否缺少节奏变化
   - Shot Duration 是否大致合理

## 输出

只输出一个 JSON 对象，不要 Markdown 代码围栏：

{
  "schema_version": "4.1",
  "episode_id": "EP002",
  "scene_id": "Scene01",
  "result": "PASS | REPLAN_REQUIRED | NEED_NEW_CAMERA",
  "scene_score": 0,
  "dimension_scores": {
    "narrative_coverage": 0,
    "shot_necessity": 0,
    "visual_differentiation": 0,
    "camera_and_motion": 0,
    "continuity": 0,
    "frozen_moment": 0,
    "rhythm": 0
  },
  "issues": [
    {
      "severity": "BLOCKER | MAJOR | MINOR",
      "shot_ids": ["ShotXX-XX"],
      "category": "string",
      "problem": "string",
      "required_change": "string"
    }
  ],
  "approved_strengths": ["string"],
  "replan_instruction": "string or null"
}

判定规则：

- PASS：没有 BLOCKER / MAJOR，且 scene_score >= 80。
- REPLAN_REQUIRED：存在导演结构问题；必须回到 Scene Planning，由 GPT Director 重规划。
- NEED_NEW_CAMERA：导演方案成立，但现有 Camera Library 无法执行关键镜头。
- 不允许在 QA JSON 中直接偷偷修改 Shot Plan。
