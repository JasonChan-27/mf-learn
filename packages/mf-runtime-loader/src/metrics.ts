type Labels = { [k: string]: string }

const DEFAULT_FLUSH_INTERVAL = 5000

let endpoint: string | null = null
let buffer: Array<any> = []
let timer: any = null
let enabled = false

export function initMetrics(opts?: {
  endpoint?: string
  flushInterval?: number
}) {
  endpoint = opts?.endpoint ?? null
  enabled = !!endpoint
  buffer = []
  if (timer) clearInterval(timer)
  if (enabled) {
    timer = setInterval(
      () => flush(),
      opts?.flushInterval ?? DEFAULT_FLUSH_INTERVAL,
    )
  }
}

export function sendMetric(name: string, value: number, labels?: Labels) {
  try {
    const item = { name, value, labels: labels ?? {}, ts: Date.now() }
    if (!enabled) {
      // Not configured: fallback to console for debugging
      if ((globalThis as any).__MF_METRICS_DEBUG__) {
        // eslint-disable-next-line no-console
        console.debug('[mf-metrics] ', item)
      }
      return
    }

    buffer.push(item)
    // if buffer large, flush immediately
    if (buffer.length >= 50) flush()
  } catch (e) {
    // noop
  }
}

export async function flush() {
  if (!enabled || !endpoint) return
  if (buffer.length === 0) return
  const payload = buffer.splice(0, buffer.length)
  try {
    await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ metrics: payload }),
    })
  } catch (e) {
    // on error, requeue
    buffer = payload.concat(buffer)
  }
}

export function shutdownMetrics() {
  if (timer) clearInterval(timer)
  flush()
}
