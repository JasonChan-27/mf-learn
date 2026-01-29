import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { initMetrics } from 'mf-telemetry'
import './index.css'
import App from './App.tsx'

try {
  if (typeof window.__MF_METRICS_ENDPOINT__ === 'string') {
    initMetrics({ endpoint: window.__MF_METRICS_ENDPOINT__ })
  }
} catch {
  // eslint-disable-next-line no-empty
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
