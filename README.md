# 校园共享设备扫码借还

Monorepo：Flutter 移动端 + Vue 管理端 + FastAPI 后端。

## 技术栈

- 移动端：Flutter 3 + Riverpod + dio + mobile_scanner
- 后端：FastAPI + SQLAlchemy 2 + Alembic + MySQL 8.0 + Redis + JWT
- 管理端：Vue 3 + Element Plus
- 部署：Docker Compose 单机

## 目录结构

```
apps/mobile/      # Flutter App（阶段 2 起）
apps/admin/       # Vue 管理端（阶段 6）
services/api/     # FastAPI 后端
deploy/           # Docker Compose 与部署配置
scripts/          # Windows 开发脚本
docs/             # 文档
```

## Windows 本地开发（阶段 1）

### 1. 启动 MySQL 8.0 与 Redis

```powershell
.\scripts\dev-up.ps1
```

### 2. 配置环境变量

复制 `deploy\.env.example` 为 `deploy\.env`，按需修改。

### 3. 安装后端依赖并迁移

需要 Python 3.10+。

```powershell
cd services\api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
cd ..\..
.\scripts\migrate.ps1
```

### 4. 启动 API

```powershell
cd services\api
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

访问：

- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/v1/health
