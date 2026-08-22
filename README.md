# 11号电竞管理系统

## 项目结构

- `frontend/`：Next.js 前台和电脑端后台页面
- `backend/`：FastAPI、SQLAlchemy、Alembic 和初始化数据
- `deploy/nginx.conf`：Nginx 反向代理示例
- `docker-compose.yml`：生产容器编排

## 本地开发

后端使用指定 Conda 环境：

```powershell
conda activate copy_page_and_Backend_Management_System
cd backend
pip install -r requirements-dev.txt
alembic upgrade head
python -m app.seed
python -m app.seed_admin
uvicorn app.main:app --reload
```

前端另开终端：

```powershell
cd frontend
npm install
npm run dev
```

开发默认管理员为 `admin` / `admin-password`，生产环境必须通过 `.env` 修改。

前台地址为 `http://127.0.0.1:3000`，后台地址为 `http://127.0.0.1:3000/admin`，后端 API 文档为 `http://127.0.0.1:8000/docs`。

### 数据库迁移说明

Alembic 是数据库结构的唯一迁移入口。每次拉取包含数据库变更的代码后，先在 `backend/` 目录执行：

```powershell
alembic upgrade head
```

如果是已有的本地 SQLite 数据库，并且其中的表已经由旧版本创建、但 Alembic 尚未记录版本，请不要删除 `esports.db`。确认表结构与当前代码一致后，执行一次：

```powershell
alembic stamp head
alembic current
```

这只会同步迁移记录，不会创建、删除或修改业务数据。之后可正常使用 `alembic upgrade head`。不要把已有数据库重新标记为旧版本（例如 `0001_initial`），否则 Alembic 会再次尝试创建已存在的表。

## Ubuntu 部署

1. 安装 Ubuntu 22.04/24.04、Docker Compose Plugin、Git 和 Nginx。
2. 克隆源码并复制环境变量：`cp .env.example .env`。
3. 修改 `.env` 中数据库密码、管理员密码和 `JWT_SECRET_KEY`，不要提交 `.env`。
4. 启动系统：`docker compose up -d --build`。
5. 查看状态：`docker compose ps`，查看日志：`docker compose logs -f backend`。
6. 将 `deploy/nginx.conf` 复制到 Nginx sites-enabled，替换域名后执行 `nginx -t && systemctl reload nginx`。
7. 使用 Certbot 为域名配置 HTTPS，并保持 `COOKIE_SECURE=true`。

后端 API 文档部署后位于 `https://你的域名/api/docs`，直接访问后端时为 `http://服务器:8000/docs`。

## 数据和文件持久化

PostgreSQL 使用 `postgres_data` Volume，游戏封面使用 `game_uploads`，工作室图片使用 `studio_uploads`。容器重启不会删除这些数据。

备份数据库：

```bash
docker compose exec -T db pg_dump -U esports esports > backup.sql
docker run --rm -v "$(basename "$PWD")_game_uploads:/data" -v "$PWD":/backup alpine tar czf /backup/game-uploads.tar.gz -C /data .
docker run --rm -v "$(basename "$PWD")_studio_uploads:/data" -v "$PWD":/backup alpine tar czf /backup/studio-uploads.tar.gz -C /data .
```

恢复数据库前停止后端写入，然后执行：

```bash
cat backup.sql | docker compose exec -T db psql -U esports esports
```

上传文件恢复到对应 Volume 后，执行 `docker compose up -d`。

## 常用维护命令

```bash
docker compose ps
docker compose logs -f backend
docker compose exec backend python -m app.seed_admin
docker compose down
```

管理员后台只针对电脑端使用；前台同时支持桌面、平板和手机。
