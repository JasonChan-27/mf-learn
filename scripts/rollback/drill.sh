#!/usr/bin/env bash
set -euo pipefail

# 回滚演练脚本（dry-run 默认）。
# 用法: drill.sh [--run]
# 如果传入 --run 则会在 CONFIRM=1 下真正执行 retag（请在 staging 环境谨慎使用）

RUN=0
if [ "${1:-}" = "--run" ]; then
  RUN=1
fi

echo "Rollback drill: listing recent tags"
git fetch --tags origin
TAGS=$(git ls-remote --tags origin | awk '{print $2}' | sed 's#refs/tags/##' | grep -v '{}' | tail -n 10)
echo "$TAGS"

LATEST_STABLE=$(echo "$TAGS" | grep -E '^v?[0-9]' | tail -n 1 || true)
if [ -z "$LATEST_STABLE" ]; then
  echo "No suitable tag found for drill"
  exit 1
fi

echo "Selected tag for drill: $LATEST_STABLE"
if [ "$RUN" -eq 0 ]; then
  echo "Dry run: would call retag.sh $LATEST_STABLE"
  ./retag.sh "$LATEST_STABLE" --no-push
  exit 0
fi

echo "Running drill: executing retag in CONFIRM mode"
CONFIRM=1 DRY_RUN=0 ./retag.sh "$LATEST_STABLE"
