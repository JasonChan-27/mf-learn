/*
 Simple webhook receiver that forwards alerts to a repository_dispatch event
 Requires environment variables: GITHUB_TOKEN, REPO_OWNER, REPO_NAME, EVENT_TYPE, SECRET (optional)
 This is a reference implementation — deploy behind auth/HTTPS in production.
*/
const express = require('express')
const fetch = require('node-fetch')
const bodyParser = require('body-parser')

const app = express()
app.use(bodyParser.json())

const PORT = process.env.PORT || 8080
const GITHUB_TOKEN = process.env.GITHUB_TOKEN
const REPO_OWNER = process.env.REPO_OWNER
const REPO_NAME = process.env.REPO_NAME
const EVENT_TYPE = process.env.EVENT_TYPE || 'alert-triggered'
const SECRET = process.env.SECRET || ''

if (!GITHUB_TOKEN || !REPO_OWNER || !REPO_NAME) {
  console.error(
    'Missing required env vars: GITHUB_TOKEN / REPO_OWNER / REPO_NAME',
  )
  process.exit(1)
}

app.post('/webhook', async (req, res) => {
  try {
    // Optionally check a simple shared secret header
    if (SECRET) {
      const sig = req.get('x-alert-secret') || ''
      if (sig !== SECRET) return res.status(401).send('invalid secret')
    }

    const payload = req.body || {}

    // Forward to GitHub repository_dispatch so a workflow can act (e.g., rollback)
    const url = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/dispatches`
    const resp = await fetch(url, {
      method: 'POST',
      headers: {
        Authorization: `token ${GITHUB_TOKEN}`,
        Accept: 'application/vnd.github.v3+json',
      },
      body: JSON.stringify({ event_type: EVENT_TYPE, client_payload: payload }),
    })

    if (!resp.ok) {
      const text = await resp.text()
      console.error('dispatch failed', resp.status, text)
      return res.status(500).send('dispatch failed')
    }

    res.status(200).send('ok')
  } catch (e) {
    console.error(e)
    res.status(500).send('error')
  }
})

app.listen(PORT, () => console.log(`webhook receiver listening ${PORT}`))
