OpenTelemetry tracing (frontend) — 快速示例

目标：把加载子应用的操作与主应用的 trace 关联，以便在 APM/Jaeger/Datadog 中追踪模块加载时延与失败。

方案要点：

- 在主应用端使用 OpenTelemetry JS（或任意支持 W3C Trace Context 的 tracer），在发起关键操作时把 `traceparent` 注入到子组件的 `props`，例如 `mount` 调用或 `loadRemote` 的 `config.props.traceparent`。
- 在 `mf-runtime-loader` 中我们会把 `config.props.traceparent` 的值附加到发送的指标上（`traceparent` 标签），并在后端或 APM 中根据该 trace id 进行合并视图。

示例（主应用 side，使用 OpenTelemetry）：

```js
import { WebTracerProvider } from '@opentelemetry/sdk-trace-web'
import {
  ConsoleSpanExporter,
  SimpleSpanProcessor,
} from '@opentelemetry/sdk-trace-base'
import { registerInstrumentations } from '@opentelemetry/instrumentation'
import { trace, context } from '@opentelemetry/api'

const provider = new WebTracerProvider()
provider.addSpanProcessor(new SimpleSpanProcessor(new ConsoleSpanExporter()))
provider.register()

const tracer = trace.getTracer('main')

function loadMicro(appConfig, el) {
  const span = tracer.startSpan('load-micro')
  const spanContext = trace.getSpanContext(span)
  // 根据 W3C Trace Context 生成 traceparent header
  const traceparent = `00-${spanContext.traceId}-${String(spanContext.spanId).padStart(16, '0')}-01`

  // 把 traceparent 透传给 loader
  appConfig.props = appConfig.props || {}
  appConfig.props.traceparent = traceparent

  try {
    // loadRemote 会把 traceparent 附加到 metrics
    mountApp(appConfig, el)
  } finally {
    span.end()
  }
}
```

注意：上面只是示意，实际使用时请用 OpenTelemetry 提供的 `getHttpTextFormat().inject()` 等 API 来生成并注入 header。
