# 灰度发布策略（参考实现）

策略概述：按最小可影响面逐步扩展流量，优先在边缘/网关做百分比分流，配合运行时特性开关与模块级灰度。

1. 流量分流点

- CDN/网关（优先）：支持百分比与条件路由。
- 前端 runtime：当网关不支持时，使用 `mf-runtime-loader` 的 `alternates` + feature flag 决定展示新/旧模块。

2. 微前端模块级灰度

- 对于子应用（`react`/`vue`），发布新版本到 `/app/vX.Y.Z/`。
- 在 `microRegistry` 中登记新版本，并利用网关或特性开关只让部分用户（按用户 ID/Cookie）加载新版本。

3. 验证与扩容

- 第一步：1-5% 流量，运行 smoke tests（登录、关键 API）。观察 10-30 分钟。
- 第二步：10-20% 流量，观察 30 分钟。
- 若稳定，继续按阶梯扩容直至 100% 或转入下一发布阶段。

4. 回滚触发条件

- 自动：5xx 错误率 > 1% 且增长幅度大于阈值，或关键路径性能退化 > 25%。
- 半自动：关键业务转化下降 > 10% 触发人工评估。

5. 关键实现要点

- `mf-runtime-loader`：支持 `timeout`、`alternates` 与 `fallback`，用于平滑回退。
- Runbook：在 `RUNBOOK.md` 中明确回滚命令、责任人与验证步骤。
- 监控：Prometheus + Alertmanager + Grafana/Sentry。
