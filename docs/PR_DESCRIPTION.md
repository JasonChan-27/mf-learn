PR Title: feat(ops): add gray-release/runbook/rollback tooling and loader fallback

Description:
This PR implements gray-release and rollback support for the monorepo:

- `packages/mf-runtime-loader`: add timeout, alternates (backup remote URLs), and tests.
- `RUNBOOK.md`: operational runbook for gray release and rollback.
- Monitoring: example Prometheus alert rules in `monitoring/ALERT_RULES_PROMETHEUS.yaml`.
- Rollback automation: `scripts/rollback/retag.sh`, `.github/workflows/rollback.yml` and `rollback-drill.yml`.
- Webhook receiver example for Alertmanager -> GitHub dispatch in `monitoring/webhook-receiver/`.

How to test locally:

1. Run package tests: `pnpm --filter mf-runtime-loader test`.
2. Simulate webhook receiver locally and post example alert (see monitoring/webhook-receiver/test-send.sh).

Notes:

- The rollback workflow requires repo dispatch permissions; add `GITHUB_TOKEN`/secrets in CI.
- See `DEPLOYMENT_GUIDE.md` and `GRAY_RELEASE_STRATEGY.md` for environment-specific steps.
