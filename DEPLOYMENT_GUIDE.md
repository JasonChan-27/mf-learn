# 部署指南（草稿）

目标：记录生产/预发布（staging）环境、网关与 CDN 配置要点，以支持灰度/回滚策略执行。

环境分层建议：
- `dev`：开发人员本地或共享 dev 环境。
- `staging`：与生产尽可能一致，用于金丝雀与回滚演练。
- `prod`：正式线上环境，配合灰度流量控制与监控告警。

网关与路由：
- 建议使用支持基于请求属性分流的网关：Envoy/Traefik/NGINX Plus/CloudLoadBalancer。
- 在网关层支持按 Header / Cookie / IP / 随机百分比分配流量到不同版本（或到不同 `microRegistry` 配置）。

CDN/静态托管：
- 采用版本化路径（如 `/react/v1.2.3/remoteEntry.js`），并保留 `current` 逻辑或在网关层路由到版本目录。
- 发布时降低 CDN TTL（短期）以便快速回滚。

CI/CD 建议：
- 每次构建产物上传到版本目录并生成 release tag（`vX.Y.Z`）。
- 在 `microRegistry` 中注册新版本并在小流量上做 Canary。
- 提供回滚脚本（`scripts/rollback/retag.sh`）与 workflow（`.github/workflows/rollback.yml`）。

Secrets/权限：
- 为 rollback workflow 提供受限 token，限于 repo:dispatch 或 tag 管理权限。
