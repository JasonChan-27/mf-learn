import { mountApp, unmountApp } from './manager'
import type { MicroAppConfig } from './types'

function getRouteContext() {
  return {
    pathname: window.location.pathname,
    query: new URLSearchParams(window.location.search),
  }
}

export function startMicroRouter(
  getContainer: (name: string) => NodeListOf<HTMLElement>,
  microRegistry: MicroAppConfig[],
) {
  async function reroute() {
    const ctx = getRouteContext()

    for (const app of microRegistry) {
      const active = app.activeWhen?.(ctx)
      const nodes = getContainer(app.name)

      nodes.forEach((el: HTMLElement) => {
        if (active && el) {
          mountApp(app, el)
        } else {
          unmountApp(app.name)
        }
      })
    }
  }

  window.addEventListener('popstate', reroute)
  reroute()
}
