import { createApp } from 'vue'
import { initMetrics } from 'mf-telemetry'
import './style.css'
import App from './App.vue'

// ;(window as any).__MF_METRICS_ENDPOINT__ = 'http://localhost:5000'

// init metrics if endpoint configured in global
try {
  if (typeof (window as any).__MF_METRICS_ENDPOINT__ === 'string') {
    initMetrics({ endpoint: (window as any).__MF_METRICS_ENDPOINT__ })
  }
} catch (e) {
  // ignore if package not available in dev
}

createApp(App).mount('#app')
