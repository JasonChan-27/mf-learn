Metrics ingestion receiver

This small service accepts POST /ingest with JSON payload { metrics: [ ... ] } and optionally forwards to Prometheus Pushgateway if `PUSHGATEWAY_URL` is set.

Run locally for testing:

```bash
cd monitoring/ingestion
node receiver.js
```

Then configure `MF_METRICS_ENDPOINT` in frontend to `http://localhost:9090/ingest` (or via your backend proxy).

Security: do not expose this endpoint publicly without authentication. In production, place behind SRE-managed API gateway.
