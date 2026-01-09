import { createApp } from 'vue'
import Home from './index.vue'
import { type MicroAppConfig } from 'mf-runtime-loader'

export const mount = (
  el: HTMLElement,
  { runtime }: MicroAppConfig['props'],
) => {
  const app = createApp(Home)
  app.mount(el)
  return () => app.unmount()
}
