export type MicroAppModule = {
  mount: (el: HTMLElement, props?: any) => () => void
}

export type MicroAppConfig = {
  name: string
  scope: string
  module: string
  url: string
  activeWhen?: (ctx: RouteContext) => boolean
  timeout?: number
  fallback?: () => HTMLElement
}

export type RouteContext = {
  pathname: string
  query: URLSearchParams
}
