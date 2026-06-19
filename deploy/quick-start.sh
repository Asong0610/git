#!/usr/bin/env bash
set -euo pipefail

# 快速启动：安装依赖 + 迁移 + 启动 API
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
API_DIR="$REPO_DIR/services/api"
ENV_FILE="$REPO_DIR/deploy/.env"

echo "快速启动校园共享设备 API ..."

cd "$API_DIR"

# 创建虚拟环境
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# 安装依赖
pip install --upgrade pip -q
pip install -e . -q

# 加载 .env
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# 迁移
echo "运行数据库迁移 ..."
alembic upgrade head

# 启动
echo "启动 API 服务（0.0.0.0:8000）..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
