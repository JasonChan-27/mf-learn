import { createRoot } from 'react-dom/client'
import DashBoard from './index'
import { type MicroAppConfig } from 'mf-runtime-loader'

export function mount(el: HTMLElement, { runtime }: MicroAppConfig['props']) {) {
  const root = createRoot(el)
  root.render(<DashBoard runtime={runtime}/>)

  return () => {
    root.unmount()
  }
}
