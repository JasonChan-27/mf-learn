# Runbook：灰度发布与回滚操作手册

## 目的与范围

本 Runbook 适用于本仓库的灰度发布与快速回滚流程，覆盖 micro-frontend（`mf-runtime-loader`）、CDN/Registry 层与后端服务回滚。目标是在最短时间内恢复线上稳定状态并减少业务影响。

## 快速回滚 - 前端（优先）

1. 将 `microRegistry` 中的当前路由回退到稳定版本（例如把 `current` 指向 `v1.2.2`）。
2. 若使用 CDN，将 `current` 目录回退或更新指向旧版本目录并清理边缘缓存。
3. 验证关键页面与业务流程。

示例命令（视具体 CI/托管而定）:

```
# 在 Git 中把 current tag 指回旧的 tag，并触发 CI 发布
git tag -f current-deploy v1.2.2
git push origin current-deploy --force

# 如果通过 CDN 管理版本目录：
# 将 /react/current/ 指向 /react/v1.2.2/（方法视 CDN 而定）
```

## 快速回滚 - 后端（Kubernetes）

```
kubectl rollout undo deployment/my-backend --to-revision=<REVISION>
kubectl rollout status deployment/my-backend
```

## 在 `packages/mf-runtime-loader` 层的回退策略

- 在 `packages/mf-runtime-loader/src/loader.ts` 中实现：
  - 模块加载超时（例如 5s）后触发回退逻辑；
  - 回退到本地内置降级模块或旧版本的 remoteEntry；
  - 上报降级事件到监控/错误收集服务。

## 监控阈值（建议）

- 5xx 错误率 > 1% 且相对基线增长 > 300% 持续 3 分钟 → 暂停灰度/触发回滚。
- 关键路径耗时（LCP/TTFB）相较基线增加 > 25% 持续 5 分钟 → 暂停灰度。
- 关键业务转化下降 > 10% → 人工评估并回滚。

## 金丝雀（Canary）发布步骤

1. 构建并上传静态产物到版本目录（/react/vX.Y.Z/）。
2. 在 `microRegistry` 中注册该版本但只对 1-5% 的用户路由到新版本（通过网关或 feature-flag）。
3. 运行自动化 smoke tests（登录、关键 API 流程）。
4. 观察监控 10-30 分钟，若无异常按 10-20% 递增流量直到 100%。

## 回滚演练（季度）

1. 在非生产环境（staging）恢复一次完整回滚；
2. 计时并记录恢复用时与遇到的问题；
3. 更新本 Runbook 与 CI 脚本。

## 联系人与职责

- 发布负责人：@release-owner
- 回滚负责人：@oncall-backend
- 监控负责人：@sre-team

## 附录：关键文件位置

- `packages/mf-runtime-loader/src/loader.ts`
- `packages/mf-runtime-loader/src/fallback.ts`
- `apps/*/vite.config.ts`（查看静态资源基路径与构建配置）

---

更新记录：

- 2026-01-23: 初始 Runbook 草稿。
