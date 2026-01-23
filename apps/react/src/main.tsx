import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { initMetrics } from 'mf-runtime-loader'
import './index.css'
import App from './App.tsx'

// Init metrics if endpoint provided globally (e.g., staging)
try {
  if (typeof (window as any).__MF_METRICS_ENDPOINT__ === 'string') {
    initMetrics({ endpoint: (window as any).__MF_METRICS_ENDPOINT__ })
  }
} catch (e) {}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
