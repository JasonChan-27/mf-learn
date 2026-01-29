import type { Metric } from './type'

const STORAGE_KEY = 'mf_telemetry_queue_v1'
const DEFAULT_FLUSH_INTERVAL = 2000
const DEFAULT_BATCH_SIZE = 20
const DEFAULT_RETRY_BASE_MS = 500

let endpoint =
  (typeof window !== 'undefined' && window.__MF_METRICS_ENDPOINT__) || ''
let queue: Metric[] = []
let flushTimer: number | null = null
let FLUSH_INTERVAL = DEFAULT_FLUSH_INTERVAL
let BATCH_SIZE = DEFAULT_BATCH_SIZE

function loadFromStorage() {
  try {
    if (typeof localStorage === 'undefined') return
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return
    const items = JSON.parse(raw) as Metric[]
    if (Array.isArray(items)) queue = items.concat(queue)
  } catch (e) {
    if (process.env.NODE_ENV !== 'production')
      console.warn('[mf-telemetry] loadFromStorage', e)
  }
}

function persistToStorage() {
  try {
    if (typeof localStorage === 'undefined') return
    localStorage.setItem(STORAGE_KEY, JSON.stringify(queue.slice(0, 1000)))
  } catch (e) {
    if (process.env.NODE_ENV !== 'production')
      console.warn('[mf-telemetry] persistToStorage', e)
  }
}

export function configure(
  opts: { endpoint?: string; flushInterval?: number; batchSize?: number } = {},
) {
  if (opts.endpoint) endpoint = opts.endpoint
  if (opts.flushInterval) FLUSH_INTERVAL = opts.flushInterval
  if (opts.batchSize) BATCH_SIZE = opts.batchSize
}

export function sendMetric(m: Metric) {
  const metric = { ...m, ts: Date.now() }
  if (!endpoint) {
    if (process.env.NODE_ENV !== 'production')
      console.debug('[mf-telemetry] metric', metric)
    return
  }
  queue.push(metric)
  persistToStorage()
  if (queue.length >= BATCH_SIZE) void flush()
  scheduleFlush()
}

function scheduleFlush() {
  if (flushTimer != null) return
  flushTimer = window.setTimeout(() => {
    flushTimer = null
    void flush()
  }, FLUSH_INTERVAL)
}

async function postWithRetry(batch: Metric[], maxRetries = 3) {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(batch),
      })
      if (!res.ok) throw new Error('non-2xx ' + res.status)
      return true
    } catch (e) {
      const wait = DEFAULT_RETRY_BASE_MS * Math.pow(2, attempt)
      if (process.env.NODE_ENV !== 'production')
        console.warn(
          `[mf-telemetry] post attempt ${attempt} failed`,
          e,
          `wait ${wait}ms`,
        )
      // last attempt fallthrough
      await new Promise((r) => setTimeout(r, wait))
    }
  }
  return false
}

export async function flush() {
  if (!endpoint) return
  if (queue.length === 0) return
  const batch = queue.splice(0, BATCH_SIZE)
  persistToStorage()
  const ok = await postWithRetry(batch, 3)
  if (!ok) {
    // restore
    queue = batch.concat(queue)
    persistToStorage()
    if (process.env.NODE_ENV !== 'production')
      console.warn('[mf-telemetry] flush failed after retries')
  }
}

export function initMetrics(opts?: {
  endpoint?: string
  flushInterval?: number
  batchSize?: number
}) {
  configure(opts || {})
  if (typeof window !== 'undefined') {
    loadFromStorage()
    window.addEventListener('beforeunload', () => {
      void flush()
    })
  }
}

// simple labels/types export
export const labels = {
  app: 'app',
  env: 'env',
  version: 'version',
} as const

export type Labels = typeof labels

export default {
  configure,
  sendMetric,
  flush,
  initMetrics,
  labels,
}
