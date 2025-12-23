import { microRegistry } from './registry'
import { mountApp, unmountApp } from './manager'

function getRouteContext() {
  return {
    pathname: window.location.pathname,
    query: new URLSearchParams(window.location.search),
  }
}

export function startMicroRouter(
  getContainer: (name: string) => HTMLElement | null,
) {
  async function reroute() {
    const ctx = getRouteContext()

    for (const app of microRegistry) {
      const active = app.activeWhen?.(ctx)
      const el = getContainer(app.name)

      if (active && el) {
        await mountApp(app, el)
      } else {
        unmountApp(app.name)
      }
    }
  }

  window.addEventListener('popstate', reroute)
  reroute()
}
