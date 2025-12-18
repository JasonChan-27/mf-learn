import { createRoot } from 'react-dom/client'
// import React from 'react'

function DashBoard() {
  return <div>DashBoard页面</div>
}

export function mount(el: HTMLElement) {
  const root = createRoot(el)
  root.render(<DashBoard />)

  return () => {
    root.unmount()
  }
}

export default DashBoard
