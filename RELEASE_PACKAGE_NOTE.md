# CatDrama Studio V4.1 Stable Package

本交付为 Phase1～Phase9 完成后的 V4.1 Stable 项目。

## 包含

- 完整源码、Episode、Schema、Runtime 与测试；
- 83 个 Master 文件及匹配的 `assets/AssetRegistry.json`；
- Phase9 GPT Director / QA 回归 Fixture；
- Phase1～Phase9 报告与正式 Workflow。

## 不包含

- `build/`：可通过 `--build` 重新生成，且包含重复 Master 副本；
- macOS `__MACOSX / .DS_Store / ._*`；
- `__pycache__ / .pyc`；
- Phase9 隔离回归产生的占位 Final、Package 和临时 Runtime State；
- 已退出 V4.1 正式链的 V2/V4 一次性 Prompt 与旧 EP002 Production 输出。

## 正式入口

项目解压后，在根目录执行：

```bash
python3.12 tools/run.py EP002 --build
python3.12 tools/run.py EP002
```

正式 EP002 仍为 `Scene01 / PLANNING / Shot Count 0`。GPT Director 负责重新规划；
测试 Fixture 不会被 Runtime 自动加载。
