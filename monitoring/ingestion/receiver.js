/*
  Simple ingestion endpoint for frontend metrics.
  Accepts POST /ingest with JSON: { metrics: [ { name, value, labels, ts } ] }
  Optional environment variable PUSHGATEWAY_URL to forward metrics in Prometheus text format.
*/
const express = require('express')
const bodyParser = require('body-parser')
const fetch = require('node-fetch')

const app = express()
app.use(bodyParser.json({ limit: '1mb' }))

const PORT = process.env.PORT || 9090
const PUSHGATEWAY = process.env.PUSHGATEWAY_URL || ''
const INGESTION_TOKEN = process.env.INGESTION_TOKEN || ''

// simple auth middleware (not used globally): expect header `Authorization: Bearer <token>`
function checkAuthHeader(req) {
  if (!INGESTION_TOKEN) return true
  const auth = req.headers['authorization'] || ''
  if (String(auth).startsWith('Bearer ')) {
    const token = String(auth).slice(7)
    return token === INGESTION_TOKEN
  }
  return false
}

function toPrometheusText(items) {
  // convert simple metrics to prometheus push format (gauge or counter approximations)
  return items
    .map((it) => {
      const labels = Object.entries(it.labels || {})
        .map(([k, v]) => `${k}="${String(v).replace(/"/g, '\\"')}"`)
        .join(',')
      return `${it.name}{${labels}} ${Number(it.value)} ${Math.floor(it.ts || Date.now())}
`
    })
    .join('')
}

app.post('/ingest', async (req, res) => {
  try {
    const body = req.body || {}
    // simple token auth (when INGESTION_TOKEN configured)
    if (!checkAuthHeader(req))
      return res.status(401).json({ ok: false, error: 'unauthorized' })
    const metrics = body.metrics || []
    console.log('received metrics:', metrics.length)

    if (PUSHGATEWAY) {
      const text = toPrometheusText(metrics)
      // push to pushgateway as a single job
      await fetch(PUSHGATEWAY, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: text,
      })
    }

    res.status(200).json({ ok: true })
  } catch (e) {
    console.error(e)
    res.status(500).json({ ok: false })
  }
})

app.get('/health', (req, res) => {
  res.json({ ok: true, pushgateway: !!PUSHGATEWAY })
})

app.listen(PORT, () => console.log(`metrics ingestion listening on ${PORT}`))
