type Metric = {
  name: string
  value?: number | string
  labels?: Record<string, string>
  ts?: number
}

const DEFAULT_ENDPOINT =
  (typeof window !== 'undefined' && (window as any).__MF_METRICS_ENDPOINT__) ||
  ''

let endpoint = DEFAULT_ENDPOINT
let queue: Metric[] = []
let flushTimer: number | null = null
const FLUSH_INTERVAL = 2000
const BATCH_SIZE = 20

export function configure(opts: { endpoint?: string } = {}) {
  if (opts.endpoint) endpoint = opts.endpoint
}

export function sendMetric(m: Metric) {
  if (!endpoint) {
    // console fallback in dev
    if (process.env.NODE_ENV !== 'production')
      console.debug('[mf-telemetry] metric', m)
    return
  }
  queue.push({ ...m, ts: Date.now() })
  if (queue.length >= BATCH_SIZE) flush()
  scheduleFlush()
}

function scheduleFlush() {
  if (flushTimer != null) return
  flushTimer = window.setTimeout(() => {
    flushTimer = null
    flush()
  }, FLUSH_INTERVAL)
}

export async function flush() {
  if (!endpoint) return
  if (queue.length === 0) return
  const batch = queue.splice(0, BATCH_SIZE)
  try {
    await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(batch),
    })
  } catch (e) {
    // if failed, put back to queue front and console.warn
    queue = batch.concat(queue)
    if (process.env.NODE_ENV !== 'production')
      console.warn('[mf-telemetry] flush failed', e)
  }
}

export function initMetrics(opts?: { endpoint?: string }) {
  configure(opts || {})
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', () => {
      // best-effort flush
      void flush()
    })
  }
}

export type { Metric }

export default {
  configure,
  sendMetric,
  flush,
  initMetrics,
}
