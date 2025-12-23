import { createApp } from 'vue'
import Home from './index.vue'

export const mount = (el: HTMLElement, props: any) => {
  const app = createApp(Home, props)
  app.mount(el)
  return () => app.unmount()
}
