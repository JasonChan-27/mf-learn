/*
 Example for collecting Web Vitals using web-vitals and posting to metrics ingestion.
 npm install web-vitals
*/
import { getCLS, getFID, getLCP, getFCP, getTTFB } from 'web-vitals'

function send(name, value, labels = {}) {
  ;(navigator.sendBeacon &&
    navigator.sendBeacon(
      '/ingest',
      JSON.stringify({ metrics: [{ name, value, labels, ts: Date.now() }] }),
    )) ||
    fetch('/ingest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        metrics: [{ name, value, labels, ts: Date.now() }],
      }),
    })
}

const labels = { app: 'main', route: location.pathname }

getCLS((metric) => send('client_cls', metric.value, labels))
getFID((metric) => send('client_fid', metric.value, labels))
getLCP((metric) => send('client_lcp_seconds', metric.value, labels))
getFCP((metric) => send('client_fcp_seconds', metric.value, labels))
getTTFB((metric) => send('client_ttfb_seconds', metric.value, labels))
