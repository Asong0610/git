#!/bin/bash
# ============================================
# 统一部署入口脚本
# 用法：bash deploy/deploy-all.sh [api|mobile|all]
# ============================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

show_help() {
    echo "用法: bash deploy-all.sh [api|mobile|all]"
    echo ""
    echo "  api     - 部署 API 后端（传统 venv + systemd 方式）"
    echo "  mobile  - 构建 Mobile Web 前端（Flutter Web 直出）"
    echo "  all     - 依次部署 API 和 Mobile"
    echo ""
    echo "示例："
    echo "  bash deploy/deploy-all.sh mobile"
    echo "  bash deploy/deploy-all.sh all"
}

case "${1:-}" in
    api)
        echo "🚀 开始部署 API 后端..."
        bash "$SCRIPT_DIR/deploy.sh"
        echo "✅ API 部署完成"
        ;;
    mobile)
        echo "🚀 开始构建 Mobile Web..."
        bash "$SCRIPT_DIR/build-mobile.sh"
        echo "✅ Mobile 构建完成"
        ;;
    all)
        echo "🚀 开始全量部署..."
        echo ""
        echo "📦 [1/2] 部署 API 后端"
        bash "$SCRIPT_DIR/deploy.sh"
        echo ""
        echo "📦 [2/2] 构建 Mobile Web"
        bash "$SCRIPT_DIR/build-mobile.sh"
        echo ""
        echo "✅ 全量部署完成"
        ;;
    *)
        show_help
        exit 1
        ;;
esac
