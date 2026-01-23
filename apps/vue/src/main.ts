import { createApp } from 'vue'
import { initMetrics } from 'mf-telemetry'
import './style.css'
import App from './App.vue'

try {
  if (typeof (window as any).__MF_METRICS_ENDPOINT__ === 'string') {
    initMetrics({ endpoint: (window as any).__MF_METRICS_ENDPOINT__ })
  }
} catch (e) {}

createApp(App).mount('#app')
