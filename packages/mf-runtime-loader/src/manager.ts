import { loadRemote } from './loader'
import type { MicroAppConfig } from './types'

const mountedApps = new Map<string, () => void>()

export async function mountApp(app: MicroAppConfig, el: HTMLElement) {
  if (mountedApps.has(app.name)) return

  try {
    const unmount = await loadRemote(el, app)
    mountedApps.set(app.name, unmount)
  } catch (e) {
    console.error(`[micro] ${app.name} load failed`, e)
    if (app.fallback) {
      el.appendChild(app.fallback())
    }
  }
}

export function unmountApp(name: string) {
  mountedApps.get(name)?.()
  mountedApps.delete(name)
}

export function unmountAll() {
  mountedApps.forEach((fn) => fn())
  mountedApps.clear()
}
