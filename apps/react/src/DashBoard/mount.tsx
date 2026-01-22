import { createRoot } from 'react-dom/client'
import DashBoard from './index'
import { RuntimeContext } from '@/constant'
import type { MicroAppConfig } from '@/types'

export function mount(
  el: HTMLElement,
  props: MicroAppConfig['props'] | undefined,
) {
  const { runtime } = props || {}
  const root = createRoot(el)
  root.render(
    <RuntimeContext.Provider value={runtime}>
      <DashBoard />
    </RuntimeContext.Provider>,
  )

  return () => {
    root.unmount()
  }
}
