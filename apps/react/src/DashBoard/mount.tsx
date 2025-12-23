import { createRoot } from 'react-dom/client'
import DashBoard from './index'

export function mount(el: HTMLElement) {
  const root = createRoot(el)
  root.render(<DashBoard />)

  return () => {
    root.unmount()
  }
}
