export type UnmountFn = () => void | Promise<void>

export type MicroAppModule = {
  mount: (el: HTMLElement, props?: any) => UnmountFn
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
