# CatDrama Studio V4.1.1 — Camera Gap Resume Upgrade

本升级包是覆盖式代码补丁，不包含也不会替换 `assets/`、Episode 剧本、
`Asset_Selection.md`、`director_state/` 或 Production 输出。

## 安装

1. 先备份当前项目。
2. 将升级包中的文件按原目录结构覆盖到当前 CatDrama Studio 项目根目录。
3. 不要用升级包替换整个项目，也不要删除已经新增的 Camera 图片。
4. 在项目根目录执行：

```bash
python3.12 tools/run.py EP002 --build
```

如果当前 Scene 正处于 Camera Gap，Build 会保留原完整 Director Plan，并生成：

```text
episodes/EP002/director_state/Scene01/CAMERA_MATCH_REQUEST.md
episodes/EP002/director_state/Scene01/Camera_Match_Result_TEMPLATE.json
```

Runtime 应显示：

```text
next_action = CAMERA_MATCH_REQUIRED
```

把最新 Production Package 和 `CAMERA_MATCH_REQUEST.md` 交给 GPT Director。保存
返回的纯 JSON 后执行：

```bash
python3.12 tools/run.py EP002 --apply-camera-match episodes/EP002/director_state/Scene01/Camera_Match_Result.json
```

成功结果为 `Camera Match Import: PASS`，下一状态必须是
`DIRECTOR_QA_REQUIRED`。Camera Match 只允许修改目标 Shot 的
`selected_camera`、`camera_status`、`camera_reason`；其他导演字段保持不变，Plan
revision 自动加一，并保留匹配前 Plan 备份。

## 安全边界

- Python 不自动选择 Camera。
- Camera 必须同时存在于 `assets/AssetRegistry.json` 和当前 Episode 的
  `Asset_Selection.md` / Build Selection。
- 未选择的 Camera ID、缺失 Shot、额外 Shot、重复 Shot 或旧 Plan revision 都会被拒绝。
- 完整 Plan Validation 仍会运行；通过后仍必须进行完整 Director QA。
- V4.1.0 的 `CAMERA_LIBRARY_REBUILT_REPLAN_REQUIRED` 状态可在下一次 `--build`
  时自动迁移，不需要重新做整场 Scene Planning。
