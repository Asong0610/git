#!/usr/bin/env bash
set -euo pipefail

# 部署 Flutter Web 到云服务器
# 用法: 在本地执行此脚本，或手动把 build/web/ 上传到服务器

SERVER_IP="111.231.77.186"
SERVER_USER="root"
WEB_DIR="/var/www/campus-device"
NGINX_CONF="/etc/nginx/sites-available/campus-device"

echo "================================"
echo "Flutter Web 部署脚本"
echo "================================"

# 1. 创建目录
echo "[1/4] 创建 Web 目录..."
ssh $SERVER_USER@$SERVER_IP "sudo mkdir -p $WEB_DIR && sudo chown \$USER:\$USER $WEB_DIR"

# 2. 上传文件
echo "[2/4] 上传 Web 文件..."
scp -r build/web/* $SERVER_USER@$SERVER_IP:$WEB_DIR/

# 3. 配置 Nginx
echo "[3/4] 配置 Nginx..."
ssh $SERVER_USER@$SERVER_IP "sudo tee $NGINX_CONF > /dev/null" << 'EOF'
server {
    listen 80;
    server_name _;
    root /var/www/campus-device;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 4. 启用站点
echo "[4/4] 启用 Nginx 站点..."
ssh $SERVER_USER@$SERVER_IP "sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/ && sudo nginx -t && sudo systemctl restart nginx"

echo ""
echo "================================"
echo "部署完成！"
echo "访问地址: http://$SERVER_IP"
echo "================================"
