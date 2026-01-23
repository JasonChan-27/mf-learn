import { createApp } from 'vue'
import { initMetrics } from 'mf-runtime-loader'
import './style.css'
import App from './App.vue'

// init metrics if endpoint configured in global
try {
  if (typeof (window as any).__MF_METRICS_ENDPOINT__ === 'string') {
    initMetrics({ endpoint: (window as any).__MF_METRICS_ENDPOINT__ })
  }
} catch (e) {
  // ignore if package not available in dev
}

createApp(App).mount('#app')
