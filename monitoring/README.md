# 监控与自动回滚说明

此目录包含示例的 Prometheus 告警规则，供 SRE 在生产环境中参考并迁移到告警系统（Prometheus Alertmanager / Grafana Alerting / Datadog 等）。

主要告警与建议动作：

- High5xxErrorRate: 5xx 错误率 > 1% 且持续 3 分钟 → 自动触发告警，人工或自动暂停灰度并回滚。
- PagePerfDegraded: 页面关键路径（LCP）较历史基线上升 > 25% → 暂停灰度并查看前端错误/资源阻塞。
- ConversionDrop: 关键业务转化率下降 > 10% → 立即人工评估并考虑回滚。

自动回滚建议实现方式：

1. Alertmanager 触发 webhook 到 CI/CD，CI/CD 触发回滚 pipeline（例如把 `microRegistry` 指回上一个稳定版本或触发 k8s rollback）。
2. 回滚 pipeline 需包含安全检查：确认回滚不会造成数据丢失或兼容性问题；回滚时降低流量并观测 5-10 分钟。

示例：用 GitOps 管理 `microRegistry` 配置时，回滚可以通过 PR 自动化把 `current` 字段指回旧版本并由 ArgoCD / Flux 应用。
