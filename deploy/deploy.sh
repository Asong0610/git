#!/usr/bin/env bash
set -euo pipefail

# ============================================
# 校园共享设备 API - 云服务器部署脚本
# 适用于 Ubuntu/Debian + MySQL 8.0 + Redis
# ============================================

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
API_DIR="$REPO_DIR/services/api"
ENV_FILE="$REPO_DIR/deploy/.env"

echo "============================================"
echo "校园共享设备 API 部署"
echo "============================================"

# Step 1: 检查 Python
echo ""
echo "[1/6] 检查 Python 环境 ..."
if ! command -v python3 &>/dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3.10+"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
echo "  Python 版本: $PYTHON_VERSION"

# Step 2: 检查 MySQL 连接
echo ""
echo "[2/6] 检查 MySQL 连接 ..."
if [ ! -f "$ENV_FILE" ]; then
    echo "错误: 未找到 $ENV_FILE"
    echo "  请复制 deploy/.env.example 为 deploy/.env 并填入你的 MySQL 连接信息"
    exit 1
fi

# 从 .env 读取 DATABASE_URL
DATABASE_URL=$(grep '^DATABASE_URL=' "$ENV_FILE" | head -1 | cut -d'=' -f2-)
if [ -z "$DATABASE_URL" ]; then
    echo "错误: .env 中未设置 DATABASE_URL"
    exit 1
fi
echo "  数据库 URL: $DATABASE_URL"

# 提取 MySQL 连接信息
# 格式: mysql+pymysql://user:pass@host:port/db
DB_USER=$(echo "$DATABASE_URL" | sed -n 's|.*://\([^:]*\):.*|\1|p')
DB_PASS=$(echo "$DATABASE_URL" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
DB_HOST=$(echo "$DATABASE_URL" | sed -n 's|.*@\([^:/]*\).*|\1|p')
DB_PORT=$(echo "$DATABASE_URL" | sed -n 's|.*@[^:]*:\([0-9]*\)/.*|\1|p')
DB_NAME=$(echo "$DATABASE_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')

echo "  主机: $DB_HOST:$DB_PORT"
echo "  用户: $DB_USER"
echo "  数据库: $DB_NAME"

# Step 3: 安装依赖
echo ""
echo "[3/6] 安装 Python 依赖 ..."
cd "$API_DIR"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
echo "  依赖安装完成"

# Step 4: 运行数据库迁移
echo ""
echo "[4/6] 运行数据库迁移 ..."
cd "$API_DIR"
source .venv/bin/activate
# 加载 .env 中的环境变量
export DATABASE_URL="$DATABASE_URL"
REDIS_URL=$(grep '^REDIS_URL=' "$ENV_FILE" | head -1 | cut -d'=' -f2-)
export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:6379/0}"
JWT_SECRET=$(grep '^JWT_SECRET=' "$ENV_FILE" | head -1 | cut -d'=' -f2-)
export JWT_SECRET="${JWT_SECRET:-change-me-in-production}"

alembic upgrade head
echo "  数据库迁移完成"

# Step 5: 安装 systemd 服务（可选）
echo ""
echo "[5/6] 配置 systemd 服务 ..."
SERVICE_FILE="/etc/systemd/system/campus-device-api.service"
if [ "$(id -u)" -eq 0 ]; then
    cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Campus Device API
After=network.target mysql.service redis.service

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$API_DIR
Environment=PATH=$API_DIR/.venv/bin
ExecStart=$API_DIR/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable campus-device-api
    echo "  systemd 服务已配置: $SERVICE_FILE"
    echo "  启动: sudo systemctl start campus-device-api"
    echo "  状态: sudo systemctl status campus-device-api"
else
    echo "  跳过 systemd 配置（需要 root 权限）"
    echo "  手动启动: cd $API_DIR && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"
fi

# Step 6: 完成
echo ""
echo "[6/6] 部署完成！"
echo ""
echo "============================================"
echo "API 地址: http://<你的服务器IP>:8000"
echo "API 文档: http://<你的服务器IP>:8000/docs"
echo "============================================"
echo ""
echo "后续步骤:"
echo "  1. 确保云服务器安全组开放 8000 端口"
echo "  2. 确保云 MySQL 安全组允许服务器 IP 连接"
echo "  3. 导入 docs/postman_collection.json 到 Postman/Apifox 进行测试"
echo "  4. 生产环境请修改 JWT_SECRET 并配置 HTTPS"
