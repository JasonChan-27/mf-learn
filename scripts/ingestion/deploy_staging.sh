#!/usr/bin/env bash
set -euo pipefail

# Usage: deploy_staging.sh <image_tag>
IMAGE_TAG=${1:-}
if [ -z "$IMAGE_TAG" ]; then
  echo "Usage: $0 <image_tag>" >&2
  exit 2
fi

echo "Deploying ingestion image $IMAGE_TAG to staging (helm)"
helm upgrade --install mf-metrics-ingestion monitoring/ingestion/helm \
  --set image.repository=${DOCKER_REGISTRY:-your-registry}/mf-metrics-ingestion \
  --set image.tag=${IMAGE_TAG} \
  --set ingestion.pushgatewayUrl=${PUSHGATEWAY_URL:-}

echo "Done"
