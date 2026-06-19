#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
API_DIR="$REPO_DIR/services/api"
ENV_FILE="$REPO_DIR/deploy/.env"

cd "$API_DIR"
source .venv/bin/activate

if [ -f "$ENV_FILE" ]; then
    export $(grep -v "^#" "$ENV_FILE" | xargs)
fi

echo "启动逾期订单扫描..."
python -m app.tasks.overdue_scanner
