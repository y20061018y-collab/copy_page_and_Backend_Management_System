# 11号电竞管理系统设计规格

## 1. 目标与范围

交付一套可部署、可维护、可移交源码的电竞服务展示系统，包括响应式前台、管理员后台、FastAPI API、PostgreSQL 数据库、Docker Compose、Nginx 配置和部署文档。

第一阶段支持四个游戏：原神、崩坏·星穹铁道、绝区零、鸣潮。前台展示游戏和服务价格，后台管理游戏、封面、服务项目、排序、启用状态和联系方式。

本阶段不实现用户注册、用户中心、订单、支付、购物车、优惠券、余额、客服、聊天、评论、消息、访问统计、复杂报表、搜索、多语言、对象存储、自动云备份、短信邮件、微信公众号和小程序。不提供永久删除，内容通过启用状态隐藏。

## 2. 技术架构

- 前端：Next.js 15、App Router、TypeScript、Tailwind CSS
- 后端：FastAPI、SQLAlchemy 2、Pydantic
- 数据库：PostgreSQL
- 迁移：Alembic
- 认证：JWT，保存于 HttpOnly Cookie
- 部署：Docker Compose
- 反向代理：Nginx
- 目标服务器：Ubuntu 22.04 LTS 或 Ubuntu 24.04 LTS

访问结构：

```text
https://客户域名.com/        前台
https://客户域名.com/admin   后台页面
https://客户域名.com/api     FastAPI 接口
```

Nginx 负责 HTTPS、域名和反向代理；Next.js 处理页面；FastAPI 处理 API；PostgreSQL 持久化数据。上传目录和数据库目录使用 Docker Volume。业务价格不写入 localStorage，所有业务数据来自 API。

## 3. 数据模型

### 3.1 AdminUser

```text
id              整数主键
username        唯一、非空
password_hash   非空
is_active       默认 true
created_at      UTC 时间
updated_at      UTC 时间
```

密码使用 Argon2 或 bcrypt 哈希，不保存明文。第一版只支持一个管理员账号体系，不提供公开注册、找回密码和多角色权限。

### 3.2 Game

```text
id              整数主键
name            游戏名称，非空
slug            唯一稳定标识，非空
tag             游戏标签
description     游戏简介
cover_image     封面访问路径
accent_color    主色
accent_color_2  辅助色
sort_order      排序值
is_active       启用状态
created_at      UTC 时间
updated_at      UTC 时间
```

`slug` 用于公开详情接口和前端稳定识别。排序值越小越靠前，禁用游戏不显示在前台。

### 3.3 GameService

```text
id              整数主键
game_id         Game 外键，非空
name            服务名称，非空
price           价格文本，非空
description     服务说明
sort_order      排序值
is_active       启用状态
created_at      UTC 时间
updated_at      UTC 时间
```

关系为 `Game 1 ─── N GameService`。价格使用字符串，以支持 `¥ 30`、`¥ 20/星`、`¥ 25/时` 和 `¥ 面议`。禁用服务不显示在前台。

### 3.4 SiteSetting

数据库只保留一条全站配置记录：

```text
id                    整数主键
site_name             网站名称
site_subtitle         网站副标题
studio_image          工作室图片访问路径，可为空
contact_wechat        微信号，可为空
contact_qq            QQ 号，可为空
contact_phone         电话，可为空
contact_description   咨询提示文字，可为空
updated_at            UTC 时间
```

为空的联系方式不渲染，全部为空时显示管理员配置提示。

## 4. 前台设计

首页 `/` 包含顶部导航、Hero 主视觉、四个游戏卡片、服务价格弹窗、联系方式弹窗和页脚。整体沿用现有原型的深色电竞风、蓝紫渐变、半透明卡片、封面背景和适度悬浮效果，并支持 `prefers-reduced-motion`。移动端不能依赖鼠标悬浮才能完成操作。

游戏卡片按 `sort_order` 展示，显示名称、标签、简介、服务标签和起始价格；点击卡片打开服务价格弹窗。弹窗桌面端居中，手机端接近全屏并可滚动，支持关闭按钮、遮罩关闭和 Escape 关闭。前台不提供编辑功能。

顶部“立即咨询”打开联系方式弹窗。已配置的微信、QQ 支持复制，电话支持复制并在手机端拨号；复制成功显示反馈。

初始素材映射：

```text
图片/原神.jpg          -> 原神
图片/崩坏·星穹铁道.jpg  -> 崩坏·星穹铁道
图片/绝区零.jpg        -> 绝区零
图片/鸣潮.jpg          -> 鸣潮
```

素材复制到 `frontend/public/images/games/`，不依赖外部图片 URL。`图片/工作室图标.jpg` 作为初始工作室图片，复制到 `frontend/public/images/studio.jpg`，并在初始化配置中写入默认路径。

## 5. 后台设计

页面路由：

```text
/admin/login
/admin
/admin/games
/admin/games/new
/admin/games/[id]
/admin/settings
```

后台桌面端使用左侧导航和顶部栏，移动端使用抽屉导航，表格在窄屏切换为卡片。

登录成功后跳转 `/admin`，JWT 放入 HttpOnly Cookie，生产环境启用 Secure 和 SameSite，默认有效期 7 天。未登录访问后台页面跳转登录页，后台写接口返回 401。登录失败使用统一错误信息，不泄露账号是否存在。退出时清理 Cookie。

`/admin` 显示游戏总数、启用游戏数、服务总数、启用服务数和最近更新时间，不做统计图表。

`/admin/games` 支持全部、启用、禁用筛选，以及新增、编辑、启用、禁用、上移、下移。禁用需二次确认，永久删除不开放。

`/admin/games/[id]` 同时编辑游戏基本信息和服务列表。游戏信息包括名称、slug、标签、简介、封面、主色、辅助色、排序值和启用状态。服务信息包括名称、价格、说明、排序值和启用状态。游戏和服务分别保存，服务支持新增、编辑、禁用、恢复、上移、下移。表单显示未保存状态，离开时提示。

封面选择后先本地预览，上传并点击保存后才正式关联。旧封面在新封面关联成功前继续有效。

`/admin/settings` 编辑网站名称、副标题、工作室图片、微信号、QQ 号、电话和咨询提示文字，采用显式保存。

工作室图片支持：

- 选择图片后本地预览
- 上传新图片
- 点击保存后正式替换前台品牌图片
- 未保存时继续使用旧图片
- 支持恢复或替换已有图片，不提供永久删除
- 前台可在顶部品牌区域和页脚使用该图片

管理员初始化命令：

```bash
docker compose exec backend python -m app.seed_admin
```

账号和密码通过环境变量提供，不开放管理员注册页面。

## 6. API 约定

公开接口：

```text
GET /api/games
GET /api/games/{slug}
GET /api/settings
```

认证接口：

```text
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

后台游戏接口：

```text
GET   /api/admin/games
POST  /api/admin/games
GET   /api/admin/games/{id}
PATCH /api/admin/games/{id}
POST  /api/admin/games/{id}/disable
POST  /api/admin/games/{id}/enable
PATCH /api/admin/games/reorder
```

后台服务接口：

```text
GET   /api/admin/games/{id}/services
POST  /api/admin/games/{id}/services
PATCH /api/admin/services/{id}
POST  /api/admin/services/{id}/disable
POST  /api/admin/services/{id}/enable
PATCH /api/admin/games/{id}/services/reorder
```

配置、上传和概览接口：

```text
GET   /api/admin/settings
PATCH /api/admin/settings
POST  /api/admin/uploads/game-cover
POST  /api/admin/uploads/studio-image
GET   /api/admin/dashboard
```

公开接口只返回启用游戏及启用服务，并按排序值升序。游戏、服务、排序和设置分别保存；前台不做长时间缓存，后台保存成功后重新拉取数据。

统一错误格式：

```json
{
  "code": "GAME_NOT_FOUND",
  "message": "游戏不存在",
  "details": {}
}
```

使用 400、401、403、404、409、413、422 和 500 表达对应错误。前端在表单附近显示校验错误，认证失效时跳转登录页并保留可恢复的表单状态。

## 7. 上传与安全

游戏封面和工作室图片支持 JPG、JPEG、PNG、WEBP，单文件最大 5MB，同时校验扩展名和 MIME 类型。服务端重新生成随机文件名：游戏封面保存到 `backend/uploads/games/`，工作室图片保存到 `backend/uploads/studio/`。数据库只保存相对访问路径，FastAPI 挂载静态目录。替换成功后清理旧图片，上传目录用 Docker Volume 持久化；未保存的新上传文件由后端清理机制处理。

登录写接口需要基础频率限制；后台写接口必须认证；CORS 只允许配置的前端域名；生产环境使用 HTTPS；`.env` 不提交 Git，提供 `.env.example`。

## 8. 工程结构与交付

```text
esports-management-system/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/images/games/
│   ├── package.json
│   └── Dockerfile
├── backend/
│   ├── app/core/
│   ├── app/models/
│   ├── app/schemas/
│   ├── app/routers/
│   ├── app/services/
│   ├── app/database.py
│   ├── app/main.py
│   ├── alembic/
│   ├── uploads/games/
│   ├── uploads/studio/
│   ├── requirements.txt
│   └── Dockerfile
├── deploy/nginx.conf
├── docker-compose.yml
├── .env.example
├── README.md
└── docs/
```

交付包括前后端源码、模型、迁移、四个游戏及完整服务初始数据、默认工作室图片、种子脚本、Docker 配置、Nginx 示例、环境变量示例、部署说明、数据库备份说明和上传文件备份说明。

数据库结构通过 `alembic upgrade head` 创建或升级，业务初始数据通过 `python -m app.seed` 导入。基本启动命令为 `docker compose up -d`。

## 9. 验收标准

- Ubuntu 服务器可按 README 完成部署
- 前台桌面端、平板端和手机端均可访问
- 前台只显示启用的四个游戏及服务
- 游戏卡片可打开价格弹窗
- 管理员可以登录、退出和访问概览
- 未登录不能修改后台数据
- 可新增、编辑、禁用、恢复游戏和服务
- 可上传、替换游戏封面
- 可在后台上传、预览、更换工作室图片，并在前台品牌区域显示
- 可调整游戏和服务排序
- 可修改联系方式并在前台显示
- 刷新前台能看到数据库最新数据
- 容器重启后数据库和上传图片不丢失
- Alembic 迁移、初始化数据和 API 文档可用
- 提供数据库及上传文件备份说明
