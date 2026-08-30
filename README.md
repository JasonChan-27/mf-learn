# CatDrama Studio V4.1

CatDrama Studio V4.1 是一个由状态驱动的 AI 短剧生产系统。

核心分工：GPT Director 负责所有创意导演决策；Python 负责确定性 State、验证、
编译、资产打包、文件 IO 与 Runtime 推进。Python 不决定 Shot 数量、Camera、
Coverage、Composition、Frozen Moment、Shot Delta 或运镜。

## 当前完成度

- Phase1：项目基线与架构审计
- Phase2-A：State Schema
- Phase2-B：Build / Reset Runtime
- Phase3：Director Plan Import
- Phase4：Director QA
- Phase5：Shot Production Runtime
- Phase6：Pure Prompt Compiler
- Phase7：Deterministic Versioned Builder
- Phase8：Official Workflow
- Phase9：EP002 Real-Asset Regression / Stable Acceptance

Phase1～Phase9 已全部完成，当前版本为 V4.1.1 Stable，并包含 Camera Gap Resume。

## 环境与入口

- 最低 Python 3.10
- 推荐 Python 3.12
- 唯一日常入口：`tools/run.py`

```bash
python3.12 tools/run.py EP002 --build
python3.12 tools/run.py EP002
```

不要用旧 V2/V4 的“一次性完整导演稿 + Prompt”流程。Runtime 会明确打印当前
`next_action`，用户只处理当前 Scene 或当前 Shot。

详细操作见：

- `00_START_HERE.md`
- `00_WORKFLOW.md`
- `director/Production_Standard.md`
- `director/STATE/V4.1_State_Architecture_Delta.md`
- `director/STATE/V4.1_Phase9_Stable_Acceptance.md`

## 稳定真相

```text
Director Plan = Shot 设计唯一来源
Shot State    = Prompt 执行唯一来源
Runtime State = 生产进度唯一来源
AssetRegistry = 资产路径与校验信息唯一来源
```

`NEED_NEW_CAMERA` 与 `NEED_ASSET` 都是显式阻塞状态。Python 不猜测、不降级、
不使用相似资产替代。

补齐 Camera 后执行 `--build`，Runtime 会保留原 Scene Director Plan 并进入
`CAMERA_MATCH_REQUIRED`；GPT Director 只补缺口机位，校验通过后重新进行 Director QA。
