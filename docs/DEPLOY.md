# 云服务器部署指南

## 前提条件

- 云服务器（Ubuntu 22.04 / Debian 12 推荐）
- 云 MySQL 8.0 实例（已创建数据库和用户）
- Redis（可安装在云服务器上或使用云 Redis）

## 1. 准备云服务器

```bash
# 安装 Python 3.10+ 和基础工具
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl

# 安装 Redis（如果用本地 Redis）
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## 2. 配置云 MySQL

在云 MySQL 控制台创建数据库和用户：

```sql
CREATE DATABASE campus_device CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'campus'@'%' IDENTIFIED BY '你的强密码';
GRANT ALL PRIVILEGES ON campus_device.* TO 'campus'@'%';
FLUSH PRIVILEGES;
```

**重要**：确保云 MySQL 的安全组/白名单允许你的云服务器 IP 连接。

## 3. 上传代码到服务器

```bash
# 方式 A：git clone（如果有仓库）
git clone <你的仓库地址> ~/xxqWORK
cd ~/xxqWORK

# 方式 B：scp 上传
# 在本地执行：
# scp -r D:\xxqWORK user@your-server:~/
```

## 4. 配置环境变量

```bash
cd ~/xxqWORK
cp deploy/.env.example deploy/.env
nano deploy/.env
```

修改 `.env` 中的关键配置：

```ini
# 改为你的云 MySQL 连接信息
DATABASE_URL=mysql+pymysql://campus:你的密码@云MySQL内网IP:3306/campus_device

# Redis（本地 Redis）
REDIS_URL=redis://127.0.0.1:6379/0

# JWT 密钥（生产环境务必修改！）
JWT_SECRET=your-random-secret-key-here-change-me

# 生产环境设置
APP_ENV=production
APP_DEBUG=false
```

## 5. 一键部署

```bash
cd ~/xxqWORK
chmod +x deploy/deploy.sh deploy/quick-start.sh

# 完整部署（含 systemd 服务配置，需要 sudo）
sudo bash deploy/deploy.sh

# 或快速启动（前台运行，适合测试）
bash deploy/quick-start.sh
```

## 6. 开放端口

在云服务器控制台的安全组中开放 **8000** 端口（TCP）。

## 7. 验证部署

```bash
# 在服务器上测试
curl http://127.0.0.1:8000/api/v1/health

# 从外部测试
curl http://你的服务器IP:8000/api/v1/health
```

访问 `http://你的服务器IP:8000/docs` 查看 Swagger API 文档。

## 8. 使用 Postman/Apifox 测试

1. 下载 `docs/postman_collection.json`
2. 导入到 Postman 或 Apifox
3. 修改集合变量 `base_url` 为 `http://你的服务器IP:8000/api/v1`
4. 按顺序运行测试场景

## 服务管理

### systemd 方式（推荐生产环境）

```bash
sudo systemctl start campus-device-api    # 启动
sudo systemctl stop campus-device-api     # 停止
sudo systemctl restart campus-device-api  # 重启
sudo systemctl status campus-device-api   # 查看状态
sudo journalctl -u campus-device-api -f   # 查看日志
```

### 手动方式

```bash
cd ~/xxqWORK/services/api
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

## 常见问题

### MySQL 连接被拒绝
- 检查云 MySQL 安全组/白名单是否包含云服务器 IP
- 确认 MySQL 用户允许从云服务器 IP 连接（`'campus'@'%'` 或指定 IP）
- 测试连接：`mysql -h 云MySQLIP -u campus -p`

### Redis 连接失败
- 确认 Redis 正在运行：`redis-cli ping`
- 检查 Redis 绑定地址：`bind 127.0.0.1`（仅本地）或 `bind 0.0.0.0`

### 端口被占用
- 修改启动命令中的 `--port` 参数
- 检查占用：`sudo lsof -i :8000`

## 生产环境建议

1. **HTTPS**：使用 Nginx 反向代理 + Let's Encrypt 证书
2. **JWT_SECRET**：使用强随机密钥（`openssl rand -hex 32`）
3. **数据库密码**：使用强密码，不要用默认值
4. **日志**：配置日志轮转，避免磁盘占满
5. **备份**：定期备份 MySQL 数据库
6. **监控**：配置健康检查和告警
