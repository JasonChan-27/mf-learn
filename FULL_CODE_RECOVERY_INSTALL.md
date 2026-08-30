# CatDrama Studio V4.1.1 — Runtime Recovery Install

这个恢复包用于修复增量补丁被当成完整目录覆盖后造成的 Python 模块缺失。

恢复包包含完整的：

- `tools/`
- `director/`
- `tests/`
- V4.1.1 根目录运行文档与配置

恢复包明确不包含，因此不会替换：

- `assets/`
- `episodes/`
- `build/`
- `bible/`
- 已生成图片、视频与 Production Package

## macOS 安装

1. 先备份当前项目。
2. 解压本恢复包。
3. 使用 `ditto` 合并恢复包，不要在 Finder 中删除或替换整个项目：

```bash
ditto "/解压位置/catdrama-studio-v4.1.1-runtime-recovery/" "/Users/yeahjason/AI/catdrama-studio 3 2/"
```

`ditto` 会覆盖同名代码文件，同时保留目标项目中恢复包未包含的资产、Episode 和
Build 文件。

## 安装验证

```bash
cd "/Users/yeahjason/AI/catdrama-studio 3 2"
test -f tools/build_shot_package.py && echo "build_shot_package.py OK"
PYTHONPATH=tools python3.12 -c "import build_shot_package, camera_match; print('Runtime imports OK')"
python3.12 tools/run.py EP002 --build
```

正常情况下，当前 Camera Gap 会进入：

```text
next_action = CAMERA_MATCH_REQUIRED
```

并生成：

```text
episodes/EP002/director_state/Scene01/CAMERA_MATCH_REQUEST.md
episodes/EP002/director_state/Scene01/Camera_Match_Result_TEMPLATE.json
```

随后把最新 Production Package 与 `CAMERA_MATCH_REQUEST.md` 交给 GPT Director，
保存 Camera Match JSON，并通过 `--apply-camera-match` 导入。
