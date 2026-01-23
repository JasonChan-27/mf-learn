#!/usr/bin/env bash
set -euo pipefail

# 用法: retag.sh <target_tag> [--no-push]
# 环境变量:
#  CONFIRM=1  # 需要显式确认才能执行推送（CI 中设置）
#  DRY_RUN=1  # 仅打印将要执行的操作，不作修改

TARGET_TAG=${1:-}
NO_PUSH=0
if [ "${2:-}" = "--no-push" ]; then
  NO_PUSH=1
fi

if [ -z "$TARGET_TAG" ]; then
  echo "Usage: $0 <target_tag> [--no-push]"
  exit 2
fi

echo "Preparing to update tag 'current-deploy' -> $TARGET_TAG"
git fetch --tags origin

# 验证目标 tag 是否存在于远端
if ! git ls-remote --tags origin | grep -q "refs/tags/$TARGET_TAG\$"; then
  echo "ERROR: target tag '$TARGET_TAG' not found on origin"
  exit 3
fi

CURRENT_TAG_LINE=$(git ls-remote --tags origin | grep "refs/tags/current-deploy" || true)
if [ -n "$CURRENT_TAG_LINE" ]; then
  echo "Current 'current-deploy' points to: $CURRENT_TAG_LINE"
fi

if [ "${DRY_RUN:-0}" != "0" ] || [ "$NO_PUSH" -eq 1 ]; then
  echo "DRY RUN: git tag -f current-deploy $TARGET_TAG"
  echo "DRY RUN: git push origin current-deploy --force"
  exit 0
fi

# 需要明确确认，避免误触
if [ "${CONFIRM:-0}" != "1" ]; then
  echo "CONFIRM env var not set to 1. Set CONFIRM=1 to allow pushing. Aborting."
  exit 4
fi

echo "Force-updating tag 'current-deploy' -> $TARGET_TAG"
git tag -f current-deploy "$TARGET_TAG"
git push origin current-deploy --force

echo "Retag complete"
