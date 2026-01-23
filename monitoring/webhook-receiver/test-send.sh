#!/usr/bin/env bash
set -euo pipefail

# Usage: ./test-send.sh <receiver-url>
# Example: ./test-send.sh http://localhost:8080/webhook

URL=${1:-http://localhost:8080/webhook}

cat <<'JSON' | curl -s -X POST -H "Content-Type: application/json" -d @- "$URL"
{
  "status": "firing",
  "alerts": [
    {
      "status": "firing",
      "labels": { "alertname": "High5xxErrorRate" },
      "annotations": { "summary": "test alert" }
    }
  ]
}
JSON

echo "sent"
