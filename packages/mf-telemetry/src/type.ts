export type Metric = {
  name: string
  value?: number | string
  labels?: Record<string, string | Record<string, unknown> | object>
  ts?: number
}
