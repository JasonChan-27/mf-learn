# Phase9 Regression Fixtures

本目录保存由 GPT Director 为 V4.1 Phase9 验收创建的 Scene01 Plan 与 Director QA
结果。

- 它们只用于自动测试与架构回归。
- `initialize_director_state()`、`--build`、`--reset` 和 Runtime 都不会自动读取本目录。
- 正式生产必须使用当前 `SCENE_PLANNING_REQUEST.md` 让 GPT Director 重新规划，
  再将结果保存到对应 Episode 的 `director_state/<Scene>/`。

