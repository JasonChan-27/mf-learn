import { createApp } from 'vue'
import Home from './index.vue'
import { RuntimeKey } from '@/constant'
import type { MicroAppConfig } from '@/types'

export const mount = (
  el: HTMLElement,
  props: MicroAppConfig['props'] | undefined,
) => {
  const { runtime } = props || {}
  const app = createApp(Home, { runtime })
  app.provide(RuntimeKey, runtime)
  app.mount(el)
  return () => app.unmount()
}
