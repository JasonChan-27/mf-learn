# mf-telemetry

轻量前端埋点客户端，批量发送、flush、可配置 endpoint。

使用示例：

import { initMetrics, sendMetric } from 'mf-telemetry'

initMetrics({ endpoint: 'https://ingest.example/api/metrics' })
sendMetric({ name: 'mf.load.attempt', labels: { app: 'vue' } })
