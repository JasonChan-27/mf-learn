import type { SharedRuntime } from 'mf-shared'

export type UnmountFn = () => void | Promise<void>

export type MicroAppModule = {
  mount: (el: HTMLElement, props?: { [key: string]: unknown }) => UnmountFn
}

export type MicroAppConfigProps = {
  runtime: SharedRuntime
  trace?: {
    traceparent?: string
  }
  [key: string]: unknown
}

export type MicroAppConfig = {
  app: string
  name: string
  scope: string
  module: string
  url: string
  alternates?: string[]
  props?: MicroAppConfigProps
  activeWhen?: (ctx: RouteContext) => boolean
  timeout?: number
  // optional loader tuning
  retryCount?: number
  // circuit breaker threshold: failures before open
  circuitThreshold?: number
  // circuit breaker open window in ms
  circuitWindowMs?: number
  fallback?: () => HTMLElement
}

export type RouteContext = {
  pathname: string
  query: URLSearchParams
}
