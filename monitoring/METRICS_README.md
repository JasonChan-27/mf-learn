Frontend metrics integration

1. Enable metrics in runtime

在主应用启动时，调用 `initMetrics` 并设置 `endpoint`：

```ts
import { initMetrics } from 'mf-runtime-loader'

initMetrics({ endpoint: 'https://metrics.example.com/ingest' })
```

或在 HTML 页面中设定全局变量 `__MF_METRICS_DEBUG__=true` 以在未配置 endpoint 时把埋点打印到控制台用于本地调试。

2. Ingestion receiver

仓库内示例接收器位于 `monitoring/ingestion/receiver.js`，启动后监听 `/ingest`。
在生产环境推荐把接收器放在内部网络并由 SRE 提供鉴权。

3. Grafana 与 Alerts

- Dashboard 模板：`monitoring/grafana/dashboard-mf-remote.json`
- Prometheus rule：`monitoring/ALERT_RULES_PROMETHEUS.yaml`
