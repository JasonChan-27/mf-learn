import { createApp } from 'vue'
import { initMetrics } from 'mf-telemetry'
import './style.css'
import App from './App.vue'

// window.__MF_METRICS_ENDPOINT__ = 'http://localhost:5000'

// init metrics if endpoint configured in global
try {
  if (typeof window.__MF_METRICS_ENDPOINT__ === 'string') {
    initMetrics({ endpoint: window.__MF_METRICS_ENDPOINT__ })
  }
} catch {
  // ignore if package not available in dev
}

createApp(App).mount('#app')
