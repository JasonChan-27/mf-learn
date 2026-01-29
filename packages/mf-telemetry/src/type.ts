declare global {
  interface Window {
    __MF_METRICS_ENDPOINT__?: string
  }
}

export type Metric = {
  name: string
  value?: number | string
  labels?: Record<string, string | Record<string, unknown> | object>
  ts?: number
}
