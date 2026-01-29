import { createApp } from 'vue'
import { initMetrics } from 'mf-telemetry'
import './style.css'
import App from './App.vue'

try {
  if (typeof window.__MF_METRICS_ENDPOINT__ === 'string') {
    initMetrics({ endpoint: window.__MF_METRICS_ENDPOINT__ })
  }
} catch {
  // eslint-disable-next-line no-empty
}

createApp(App).mount('#app')
