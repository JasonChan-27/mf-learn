# EP002 Scene01 — Camera Match Resume Request

当前不是重新规划 Scene。只解决已经锁定的 Director Plan 中的 Camera Gap。

请读取最新 Production Context Package、实际 Camera Master 图片，以及下面的恢复数据。

## 恢复数据

```json
{
  "source_plan": "episodes/EP002/director_state/Scene01/Scene_Director_Plan_RESULT.json",
  "source_plan_revision": 1,
  "camera_gap_shots": [
    {
      "shot_id": "Shot01-02",
      "narrative_purpose": "让大漂亮以认真担忧的怀中表演完成第一层离别演技，建立她情绪投入最快、最主动的角色差异。",
      "primary_focus": "大漂亮在小南怀中的认真担忧表演",
      "coverage": "MEDIUM_CLOSE",
      "coverage_reason": "中近景可同时保留大漂亮完整头胸、前爪与小南抱持它的双臂及部分面部反应，让猫的表演和人猫关系同等清晰，而不塞入其余角色。",
      "composition_intent": "大漂亮占画面主要视觉面积并位于小南怀中上扬视线，小南的下半张脸、眼神和双臂作为关系框架进入画面；入户门或木质门框以柔焦背景维持玄关身份，小帅与阿诺完全退出画面。",
      "camera_requirement": {
        "purpose": "读取怀中单猫的认真担忧表情与小南被打动前的细小反应",
        "scale": "MEDIUM_CLOSE",
        "subject_zone": "入户门前小南上半身与怀中猫咪区域",
        "axis_requirement": "保持 Camera01 已建立的室内朝门方向及大漂亮仰视小南的视线关系，不从门外反拍",
        "lens_intent": "适度压缩背景并突出猫眼、耳位和抱持关系，保持自然面部与毛发比例"
      },
      "current_selected_camera": null,
      "current_camera_status": "NEED_NEW_CAMERA",
      "current_camera_reason": "当前 Asset Selection 只有面向整段玄关的 Camera01；其固定低位中大全景不能稳定提供小南上半身与怀中大漂亮的中近景表演读取，且不得以裁切或临时改镜头替代未登记的互动 Camera Master。",
      "camera_motion": "LOCKED_OFF",
      "camera_motion_reason": "台词的笑点来自大漂亮过度认真的静态凝视与小南半拍发愣，锁定画面比推近更能保留克制观察感。",
      "axis_status": "PRESERVED",
      "continuity_mode": "CAMERA_CUT_CONTINUITY"
    },
    {
      "shot_id": "Shot01-03",
      "narrative_purpose": "让小帅用抱腿和颤抖语气把大漂亮的安全提醒升级成“可能永远回不来”，完成第二层更夸张的离别演技。",
      "primary_focus": "小帅靠近并抱住小南腿部的悲情加码",
      "coverage": "MEDIUM",
      "coverage_reason": "低机位中景可以完整显示小帅身体、前爪与小南小腿之间的真实接触，并保留足够地面空间说明它不是拟人站立。",
      "composition_intent": "小帅位于画面下半部主焦点，后爪和身体重量明确落在地面，双前爪短暂贴住小南一侧小腿；小南只以膝下腿部进入画面形成尺度和依附关系，背景保留门口地垫或鞋柜边缘作为空间锚点。",
      "camera_requirement": {
        "purpose": "清楚验证小帅从四爪着地到前爪抱腿的真实猫咪动作，并读取仰视表演",
        "scale": "MEDIUM",
        "subject_zone": "小南脚边及门前猫咪活动地面",
        "axis_requirement": "保持 Camera01 的门内主轴和小帅朝向小南的屏幕方向，不绕到小南腿部另一侧反打",
        "lens_intent": "自然呈现猫体和人腿比例，避免超广角把猫头、爪或小南腿部夸张变形"
      },
      "current_selected_camera": null,
      "current_camera_status": "NEED_NEW_CAMERA",
      "current_camera_reason": "Camera01 虽为低位，但覆盖过宽且主体区面向完整玄关，无法稳定把小帅、前爪与小南小腿组织成可验证的中景；当前 Registry/Selection 未提供脚边互动 Camera Master，必须补充后再锁定。",
      "camera_motion": "LOCKED_OFF",
      "camera_motion_reason": "抱腿动作和颤抖台词本身承担升级，固定低机位可让真实接触边界清晰，避免跟拍造成拟人站立或爪部错位。",
      "axis_status": "PRESERVED",
      "continuity_mode": "CAMERA_CUT_CONTINUITY"
    },
    {
      "shot_id": "Shot01-05",
      "narrative_purpose": "让小南从短暂感动转为忍笑，以摸头回应三猫的心意，再用“只是出去取个快递”完成生活化真相揭示。",
      "primary_focus": "小南从动容到忍笑并温柔揭示只是取快递",
      "coverage": "MEDIUM_CLOSE",
      "coverage_reason": "中近景可覆盖小南面部、上身、抱持双臂和大漂亮头部，让情绪渐变、摸头接触与两句台词同时可读，并主动排除脚边复杂动作。",
      "composition_intent": "小南面部与大漂亮头部形成上下双焦点，小南一只手从抱持位置移到大漂亮头顶；门的木质色块柔焦留在背景，脚边小帅和地面阿诺均不进入画面，视线重点保持在小南的克制笑意。",
      "camera_requirement": {
        "purpose": "读取小南情绪渐变、摸头接触与怀中大漂亮的近距离反应",
        "scale": "MEDIUM_CLOSE",
        "subject_zone": "入户门前小南上半身与怀中猫咪区域",
        "axis_requirement": "沿用 Shot01-02 所需的室内朝门互动轴，不从大漂亮视线反侧越轴",
        "lens_intent": "自然压缩背景并保留人脸、手和猫头的真实比例，重点分离眼神与触摸"
      },
      "current_selected_camera": null,
      "current_camera_status": "NEED_NEW_CAMERA",
      "current_camera_reason": "此镜可与 Shot01-02 共用同一新增的怀中人猫互动中近景 Camera Master，但当前 Asset Selection 未登记该机位；Camera01 无法稳定读取面部渐变与摸头接触，因此不能标为匹配。",
      "camera_motion": "LOCKED_OFF",
      "camera_motion_reason": "小南先动容、再忍笑、最后平静揭示的表演需要稳定观察，额外推近会把生活化反差处理得过度煽情。",
      "axis_status": "PRESERVED",
      "continuity_mode": "CAMERA_CUT_CONTINUITY"
    }
  ],
  "selected_camera_candidates": [
    {
      "id": "cameras.entrance-hall-camera01",
      "name": "Entrance Hall camera01",
      "path": "assets/cameras/Entrance Hall camera01.png",
      "aliases": [
        "Entrance Hall camera01"
      ],
      "tags": [
        "cameras"
      ],
      "package_path": "assets/cameras/cameras__entrance-hall-camera01.png",
      "currently_used_in_plan": true
    },
    {
      "id": "cameras.entrance-hall-camera02",
      "name": "Entrance Hall camera02",
      "path": "assets/cameras/Entrance Hall camera02.png",
      "aliases": [
        "Entrance Hall camera02"
      ],
      "tags": [
        "cameras"
      ],
      "package_path": "assets/cameras/cameras__entrance-hall-camera02.png",
      "currently_used_in_plan": false
    },
    {
      "id": "cameras.entrance-hall-camera03",
      "name": "Entrance Hall camera03",
      "path": "assets/cameras/Entrance Hall camera03.png",
      "aliases": [
        "Entrance Hall camera03"
      ],
      "tags": [
        "cameras"
      ],
      "package_path": "assets/cameras/cameras__entrance-hall-camera03.png",
      "currently_used_in_plan": false
    },
    {
      "id": "cameras.living-room-camera06",
      "name": "Living Room Camera06",
      "path": "assets/cameras/Living Room Camera06.png",
      "aliases": [
        "Living Room Camera06"
      ],
      "tags": [
        "cameras"
      ],
      "package_path": "assets/cameras/cameras__living-room-camera06.png",
      "currently_used_in_plan": false
    },
    {
      "id": "cameras.dining-room-camera-02",
      "name": "Dining Room Camera 02",
      "path": "assets/cameras/Dining Room Camera 02.png",
      "aliases": [
        "Dining Room Camera 02"
      ],
      "tags": [
        "cameras"
      ],
      "package_path": "assets/cameras/cameras__dining-room-camera-02.png",
      "currently_used_in_plan": false
    },
    {
      "id": "cameras.dining-room-camera-05",
      "name": "Dining Room Camera 05",
      "path": "assets/cameras/Dining Room Camera 05.png",
      "aliases": [
        "Dining Room Camera 05"
      ],
      "tags": [
        "cameras"
      ],
      "package_path": "assets/cameras/cameras__dining-room-camera-05.png",
      "currently_used_in_plan": false
    }
  ]
}
```

## 导演任务

1. 逐一检查每个 Camera Gap Shot 的叙事目的、Coverage、Composition、Axis、Motion 与 Continuity。
2. 只从 selected_camera_candidates 中选择实际可执行的 Camera Master ID。
3. Camera 选择、MATCH / PARTIAL_MATCH 判定和 camera_reason 必须由 GPT Director 明确决定。
4. 不改变 Shot 数量、顺序、Coverage、Composition、Camera Motion、Axis、Continuity、动作、Frozen Moment 或任何非 Camera 匹配字段。
5. 每个 Camera Gap Shot 必须恰好输出一项 resolution，不得遗漏或增加 Shot。

只输出符合 director/STATE/Camera_Match_Result.schema.json 的纯 JSON；不要 Markdown 代码围栏，不要 IMAGE PROMPT / VIDEO PROMPT，不要内部推理。

输出结构：

```json
{
  "schema_version": "4.1",
  "episode_id": "EP002",
  "scene_id": "Scene01",
  "source_plan_revision": 1,
  "resolutions": [
    {
      "shot_id": "Shot01-02",
      "selected_camera": "",
      "camera_status": "MATCH",
      "camera_reason": ""
    },
    {
      "shot_id": "Shot01-03",
      "selected_camera": "",
      "camera_status": "MATCH",
      "camera_reason": ""
    },
    {
      "shot_id": "Shot01-05",
      "selected_camera": "",
      "camera_status": "MATCH",
      "camera_reason": ""
    }
  ]
}
```
