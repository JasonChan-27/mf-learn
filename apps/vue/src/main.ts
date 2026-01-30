import { createApp } from 'vue'
import { initMetrics } from 'mf-telemetry'
import './style.css'
import App from './App.vue'

try {
  if (typeof window.__MF_METRICS_ENDPOINT__ === 'string') {
    initMetrics({ endpoint: window.__MF_METRICS_ENDPOINT__ })
  }
} catch {
  // ignore
}

console.log(`
createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})
`)

createApp(App).mount('#app')
