#!/bin/bash
# Mobile Web 构建脚本
# 功能：构建 Flutter Web 并直出到 Nginx 静态目录
# 用法：bash deploy/build-mobile.sh

set -e

FLUTTER=/opt/flutter/bin/flutter
PROJECT_DIR=/root/project/xxqWORK/apps/mobile
OUTPUT_DIR=/root/project/web/mobile

echo "📦 开始构建 Mobile Web..."

cd "$PROJECT_DIR"

# 清理旧构建产物
echo "🧹 清理旧构建产物..."
rm -rf build/web

# 获取依赖
echo "📥 获取 Flutter 依赖..."
$FLUTTER pub get

# 构建 Web（直出到目标目录）
echo "🔨 构建 Web（base-href=/mobile/，直出到 $OUTPUT_DIR）..."
$FLUTTER build web \
  --base-href /mobile/ \
  --output "$OUTPUT_DIR"

echo "✅ Mobile Web 构建完成！"
echo "📂 输出目录：$OUTPUT_DIR"
ls -lh "$OUTPUT_DIR" | head -15
