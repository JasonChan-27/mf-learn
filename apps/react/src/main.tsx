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
  // ignore
}

console.log(`
<BrowserRouter basename={import.meta.env.BASE_URL}>
`)

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
