# 11 号电竞管理系统：生产部署与更新手册

本文用于将本项目部署到 Ubuntu 22.04/24.04 服务器，并安全地更新已有部署。

> 当前已确认的线上环境：登录用户为 `ubuntu`，运行中的 Compose 项目目录为 `/home/ubuntu/esports-system-utf8`。该目录中的容器名称为 `esports-system-utf8-backend-1`、`esports-system-utf8-db-1` 与 `esports-system-utf8-frontend-1`。

## 0. 重要约定与安全边界

### 部署信息

| 项目 | 当前值 |
| --- | --- |
| 本机工作目录 | `D:\Code\orca\workspaces\copy_page_and_Backend_Management_System\new-feature` |
| Git 仓库 | `https://github.com/y20061018y-collab/copy_page_and_Backend_Management_System.git` |
| 当前开发分支 | `y20061018y-collab/new-feature` |
| 服务器登录用户 | `ubuntu` |
| 服务器项目目录 | `/home/ubuntu/esports-system-utf8` |
| 前端容器端口 | `3000` |
| 后端容器端口 | `8000` |
| 生产入口 | Nginx（80 / 443 端口） |

服务器使用 Docker named volumes 持久化数据：

- PostgreSQL 数据库：`esports-system-utf8_postgres_data`
- 游戏封面：`esports-system-utf8_game_uploads`
- 工作室图片：`esports-system-utf8_studio_uploads`

`docker compose up -d --build` 仅重建应用容器，**不会删除上述 Volume**。但是以下命令可能导致不可恢复的数据丢失，生产环境不要执行：

```bash
# 不要在生产环境执行
docker compose down -v
docker volume rm esports-system-utf8_postgres_data
docker system prune -a --volumes
git clean -fdx
```

`.env` 含数据库密码、管理员密码和 JWT 密钥，已在 `.gitignore` 中忽略。不得提交、粘贴到聊天记录或上传到仓库。

## 1. 发布前：在本机提交并推送代码

服务器只能拉取已经推送到 GitHub 的提交。先在 Windows PowerShell 中进入项目目录：

```powershell
cd D:\Code\orca\workspaces\copy_page_and_Backend_Management_System\new-feature
git status
git branch --show-current
git remote -v
```

确认当前分支是 `y20061018y-collab/new-feature`，且 `git status` 中列出的文件都是本次要发布的改动。

### 1.1 提交所有已确认的改动

仅在所有未提交改动都应发布时使用：

```powershell
git add -A
git commit -m "feat: describe this release"
git push -u origin y20061018y-collab/new-feature
```

### 1.2 只提交指定文件

若工作区还有其他未完成改动，不要使用 `git add -A`。改为逐个添加本次发布的文件，例如按钮样式修复：

```powershell
git add frontend/app/globals.css
git add frontend/app/admin/page.tsx
git add frontend/app/admin/games/page.tsx
git commit -m "fix: center add-game button content"
git push -u origin y20061018y-collab/new-feature
```

### 1.3 本机检查

至少执行与改动范围相符的检查。前端 TypeScript 检查：

```powershell
cd frontend
npm run typecheck
cd ..
```

确认远程仓库已有刚推送的提交：

```powershell
git log -1 --oneline
git ls-remote --heads origin y20061018y-collab/new-feature
```

## 2. 登录服务器与确认运行目录

在 Windows PowerShell 中使用服务器公网 IP 或域名登录：

```powershell
ssh ubuntu@<服务器公网IP或域名>
```

使用私钥时：

```powershell
ssh -i C:\Users\<你的Windows用户名>\.ssh\<私钥文件>.pem ubuntu@<服务器公网IP或域名>
```

登录后，不要凭猜测进入目录。通过正在运行的 Docker 容器确认线上目录：

```bash
sudo docker ps --format '{{.Names}}  {{.Label "com.docker.compose.project.working_dir"}}'
```

当前环境应显示：

```text
esports-system-utf8-backend-1  /home/ubuntu/esports-system-utf8
esports-system-utf8-db-1  /home/ubuntu/esports-system-utf8
esports-system-utf8-frontend-1  /home/ubuntu/esports-system-utf8
```

若报错 `permission denied while trying to connect to the Docker API`，表示 Docker 服务通常已运行，但当前用户尚无 socket 访问权限。可临时在 Docker 命令前加 `sudo`；也可为当前用户配置权限：

```bash
sudo usermod -aG docker $USER
exit
```

重新 SSH 登录后执行 `docker ps` 验证。Docker group 拥有接近 root 的权限，只应授予可信的运维用户。

## 3. 首次部署到新服务器

以下流程适用于一台尚未部署本项目的新 Ubuntu 服务器。若当前服务器已经在运行 `/home/ubuntu/esports-system-utf8`，请跳到第 4 节，不要重新克隆到其他目录。

### 3.1 安装运行依赖

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-plugin nginx curl
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

执行后退出并重新登录，以使 Docker group 生效：

```bash
exit
```

### 3.2 克隆指定分支

重新登录后执行：

```bash
git clone --branch y20061018y-collab/new-feature \
  https://github.com/y20061018y-collab/copy_page_and_Backend_Management_System.git \
  ~/esports-system-utf8
cd ~/esports-system-utf8
git status
```

如果仓库为私有仓库且 HTTPS 要求认证，请使用具有仓库读取权限的 GitHub Fine-grained Personal Access Token，或为服务器配置只读 Deploy Key；不要将令牌写入命令历史、仓库文件或 Docker Compose 文件。

### 3.3 创建生产环境变量

```bash
cd ~/esports-system-utf8
cp .env.example .env
chmod 600 .env
nano .env
```

至少修改以下值：

```dotenv
POSTGRES_PASSWORD=<高强度且唯一的数据库密码>
DATABASE_URL=postgresql+psycopg://esports:<与上方相同的密码>@db:5432/esports
JWT_SECRET_KEY=<至少32字节的随机密钥>
ADMIN_USERNAME=<生产管理员用户名>
ADMIN_PASSWORD=<高强度管理员密码>
COOKIE_SECURE=true
```

可以在服务器本地生成 JWT 密钥，然后仅复制输出到 `.env`：

```bash
openssl rand -hex 32
```

确保 `POSTGRES_PASSWORD` 和 `DATABASE_URL` 中的密码完全一致。若密码包含 `@`、`:`、`/` 等 URL 特殊字符，需要进行 URL 编码；最简单的做法是使用不含这些符号、但足够长且随机的密码。

### 3.4 构建并启动容器

```bash
cd ~/esports-system-utf8
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 backend
```

后端容器启动命令会自动执行：

```text
alembic upgrade head && python -m app.seed && python -m app.seed_admin
```

因此首次启动及后续部署都会自动应用数据库迁移。不要在生产库上手工删除 Alembic 表或伪造迁移版本。

### 3.5 本机健康检查

```bash
curl -fsS http://127.0.0.1:3000/ > /dev/null && echo "frontend OK"
curl -fsS http://127.0.0.1:8000/docs > /dev/null && echo "backend OK"
```

若任一命令无输出或报错，查看对应日志：

```bash
docker compose logs --tail=200 frontend
docker compose logs --tail=200 backend
docker compose logs --tail=200 db
```

## 4. 将当前手工部署目录迁移为 Git 管理（仅执行一次）

已确认当前线上目录 `/home/ubuntu/esports-system-utf8` 不是 Git 仓库，因此在该目录执行 `git pull` 会出现：

```text
fatal: not a git repository (or any of the parent directories): .git
```

本节会把该目录绑定到远程仓库和发布分支。`git reset --hard` 会覆盖**项目源码文件**，因此必须先备份；它不会删除 Docker named volumes，但本节仍会备份 `.env` 和源码目录。

### 4.1 备份当前源码与环境变量

```bash
cd ~
test -f esports-system-utf8/.env
cp --preserve=mode esports-system-utf8/.env .esports-system-utf8.env.backup
tar -czf "esports-system-utf8-before-git-$(date +%Y%m%d-%H%M%S).tar.gz" esports-system-utf8
ls -lh .esports-system-utf8.env.backup esports-system-utf8-before-git-*.tar.gz
```

若 `test -f` 返回失败，先停止操作，确认 `.env` 实际位置后再继续。不要用示例 `.env` 覆盖已有生产 `.env`。

### 4.2 初始化 Git 并检出发布代码

此步骤假设已按第 1 节把 `y20061018y-collab/new-feature` 推送到 GitHub。

```bash
cd ~/esports-system-utf8
git init
git remote add origin https://github.com/y20061018y-collab/copy_page_and_Backend_Management_System.git
git fetch --prune origin
git reset --hard origin/y20061018y-collab/new-feature
git switch -C deploy --track origin/y20061018y-collab/new-feature
git status
git branch -vv
```

预期：`git status` 显示工作区干净，`deploy` 分支追踪 `origin/y20061018y-collab/new-feature`。

如果 `git remote add origin` 提示 origin 已存在，核对地址后再继续：

```bash
git remote -v
```

只有在地址错误时才修正：

```bash
git remote set-url origin https://github.com/y20061018y-collab/copy_page_and_Backend_Management_System.git
```

### 4.3 确认生产环境变量仍存在

`.env` 被 Git 忽略，正常情况下仍应存在。验证而不显示其中的敏感值：

```bash
cd ~/esports-system-utf8
test -f .env && echo ".env exists"
stat -c '%a %n' .env
```

如果 `.env` 丢失，从刚才的备份恢复：

```bash
cp --preserve=mode ~/.esports-system-utf8.env.backup .env
chmod 600 .env
```

### 4.4 构建并切换到新版本

```bash
cd ~/esports-system-utf8
sudo docker compose config
sudo docker compose up -d --build
sudo docker compose ps
sudo docker compose logs --tail=100 backend
```

完成第 4 节后，今后的部署使用第 5 节即可。

## 5. 日常更新部署流程

每次发布按顺序执行。更新前应当已经在本机完成第 1 节的提交、检查和 `git push`。

### 5.1 登录并检查远程更新

```bash
ssh ubuntu@<服务器公网IP或域名>
cd ~/esports-system-utf8
git status --short
git fetch --prune origin
git log --oneline HEAD..@{upstream}
```

说明：

- `git status --short` 应无输出。若有输出，先查明服务器本地改动的来源；不要直接覆盖。
- `git log --oneline HEAD..@{upstream}` 会显示待部署的新提交。无输出表示服务器已是最新代码。

### 5.2 更新前备份数据

后端含数据库迁移、删除数据或大版本更新时必须备份。普通纯前端样式更新也建议保留最近备份。

```bash
cd ~/esports-system-utf8
backup_dir="$HOME/backups/esports-system-utf8/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup_dir"

sudo docker compose exec -T db pg_dump -U esports esports > "$backup_dir/database.sql"
sudo docker run --rm \
  -v esports-system-utf8_game_uploads:/data \
  -v "$backup_dir":/backup \
  alpine tar czf /backup/game-uploads.tar.gz -C /data .
sudo docker run --rm \
  -v esports-system-utf8_studio_uploads:/data \
  -v "$backup_dir":/backup \
  alpine tar czf /backup/studio-uploads.tar.gz -C /data .

ls -lh "$backup_dir"
```

确认至少存在 `database.sql`、`game-uploads.tar.gz` 和 `studio-uploads.tar.gz` 后，再继续更新。

### 5.3 拉取、构建并启动

```bash
cd ~/esports-system-utf8
git pull --ff-only
sudo docker compose config
sudo docker compose up -d --build
sudo docker compose ps
```

`--ff-only` 会在服务器历史与远程分支发生分叉时安全地拒绝更新，不会自动生成难以审计的 merge commit。出现拒绝时不要改用普通 `git pull`；先检查：

```bash
git status
git log --oneline --decorate --graph --all -20
```

### 5.4 部署后验证

```bash
cd ~/esports-system-utf8
sudo docker compose logs --tail=150 backend
sudo docker compose logs --tail=100 frontend
curl -fsS http://127.0.0.1:3000/ > /dev/null && echo "frontend OK"
curl -fsS http://127.0.0.1:8000/docs > /dev/null && echo "backend OK"
```

还应在浏览器中检查：

1. 首页可打开，静态资源不报 404；
2. `/admin` 可打开且管理员能登录；
3. 本次改动对应页面和交互正常；
4. 若涉及数据结构，确认后台读写和图片上传正常。

若容器状态不是 `Up`，立即查看日志而不是反复重启：

```bash
sudo docker compose ps
sudo docker compose logs --tail=300 backend
sudo docker compose logs --tail=300 frontend
sudo docker compose logs --tail=300 db
```

## 6. 配置 Nginx 与 HTTPS（首次配置或域名变更时）

项目提供了示例反向代理配置 `deploy/nginx.conf`。它将：

- `/` 代理到 Next.js 前端（`127.0.0.1:3000`）；
- `/api/`、`/api/docs`、`/api/openapi.json` 和 `/uploads/` 代理到 FastAPI（`127.0.0.1:8000`）。

复制配置前先检查现有站点，避免覆盖别的业务：

```bash
sudo ls -la /etc/nginx/sites-available /etc/nginx/sites-enabled
```

创建独立站点配置：

```bash
cd ~/esports-system-utf8
sudo cp deploy/nginx.conf /etc/nginx/sites-available/esports-system
sudo nano /etc/nginx/sites-available/esports-system
```

将其中的：

```nginx
server_name example.com;
```

替换为实际域名，例如：

```nginx
server_name example.com www.example.com;
```

确认域名 DNS 已指向此服务器公网 IP 后启用配置并验证：

```bash
sudo ln -s /etc/nginx/sites-available/esports-system /etc/nginx/sites-enabled/esports-system
sudo nginx -t
sudo systemctl reload nginx
```

只有 `nginx -t` 显示成功时才能 reload。若提示 80 端口或 `server_name` 冲突，先检查现有配置，切勿删除不属于本项目的站点文件。

安装并申请 HTTPS 证书：

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d <你的域名>
sudo systemctl status certbot.timer
```

HTTPS 启用后，`.env` 必须保持：

```dotenv
COOKIE_SECURE=true
```

## 7. 回滚

### 7.1 仅回滚应用代码

先找出已知正常的 commit：

```bash
cd ~/esports-system-utf8
git log --oneline --decorate -20
```

确认目标 commit 后，将源码回到该版本并重建容器：

```bash
git reset --hard <已知正常的commit哈希>
sudo docker compose up -d --build
sudo docker compose ps
sudo docker compose logs --tail=150 backend
```

这只回滚代码。若刚才的发布包含 Alembic 数据库迁移，数据库不会自动降级；旧代码是否能兼容新结构需要根据该迁移评估。不要擅自执行 `alembic downgrade`。

恢复到远程最新发布版本：

```bash
git fetch origin
git reset --hard @{upstream}
sudo docker compose up -d --build
```

### 7.2 恢复数据库与上传文件

此操作会覆盖当前业务数据，只在确认备份和恢复目标无误后执行。先暂停后端写入：

```bash
cd ~/esports-system-utf8
sudo docker compose stop backend
```

恢复数据库（将路径替换为实际备份目录）：

```bash
cat "$HOME/backups/esports-system-utf8/<时间戳>/database.sql" \
  | sudo docker compose exec -T db psql -U esports esports
```

恢复上传文件前，请先单独备份当前 Volume；再解压目标备份：

```bash
backup_dir="$HOME/backups/esports-system-utf8/<时间戳>"
sudo docker run --rm \
  -v esports-system-utf8_game_uploads:/data \
  -v "$backup_dir":/backup \
  alpine sh -c 'rm -rf /data/* && tar xzf /backup/game-uploads.tar.gz -C /data'
sudo docker run --rm \
  -v esports-system-utf8_studio_uploads:/data \
  -v "$backup_dir":/backup \
  alpine sh -c 'rm -rf /data/* && tar xzf /backup/studio-uploads.tar.gz -C /data'

sudo docker compose up -d
sudo docker compose ps
```

上述两条恢复上传文件的命令会清空对应 Volume 的当前文件后再恢复，务必先确认备份目录正确。

## 8. 常见故障排查

### Docker 权限错误

错误：

```text
permission denied while trying to connect to the Docker API at unix:///var/run/docker.sock
```

处理：本次会话改用 `sudo docker ...`；长期方案执行 `sudo usermod -aG docker $USER` 后退出并重新登录。

### `git pull` 提示不是 Git 仓库

错误：

```text
fatal: not a git repository (or any of the parent directories): .git
```

说明目录是手工上传副本。仅对当前已确认的线上目录执行第 4 节的一次性迁移。

### 后端容器反复重启

```bash
cd ~/esports-system-utf8
sudo docker compose ps
sudo docker compose logs --tail=300 backend
sudo docker compose logs --tail=300 db
```

常见原因：`.env` 中密码不一致、数据库未健康、迁移失败、端口被占用。不要删除数据库 Volume 来“修复”迁移错误。

### 前端页面未更新

```bash
cd ~/esports-system-utf8
git log -1 --oneline
sudo docker compose build --no-cache frontend
sudo docker compose up -d frontend
sudo docker compose logs --tail=100 frontend
```

确认 Git commit 正确后再使用无缓存构建；大多数正常发布不需要 `--no-cache`。

### Nginx 返回 502

```bash
sudo systemctl status nginx --no-pager
sudo nginx -t
curl -I http://127.0.0.1:3000/
curl -I http://127.0.0.1:8000/docs
sudo tail -n 100 /var/log/nginx/error.log
```

先确认前、后端容器正常，再检查 Nginx 配置；不要仅通过重启 Nginx 掩盖应用容器故障。

## 9. 每次发布的最短清单

本机：

```powershell
cd D:\Code\orca\workspaces\copy_page_and_Backend_Management_System\new-feature
git status
git add <本次发布的文件>
git commit -m "说明本次更新"
git push origin y20061018y-collab/new-feature
```

服务器：

```bash
ssh ubuntu@<服务器公网IP或域名>
cd ~/esports-system-utf8
git status --short
git pull --ff-only
sudo docker compose up -d --build
sudo docker compose ps
sudo docker compose logs --tail=100 backend
```
