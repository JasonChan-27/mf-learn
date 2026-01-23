#!/usr/bin/env bash
set -euo pipefail

# 用法: retag.sh <target_tag>
TARGET_TAG=${1:-}
if [ -z "$TARGET_TAG" ]; then
  echo "Usage: $0 <target_tag>"
  exit 2
fi

echo "Force-updating tag 'current-deploy' -> $TARGET_TAG"
git fetch --tags origin
git tag -f current-deploy "$TARGET_TAG"
git push origin current-deploy --force

echo "Retag complete"
