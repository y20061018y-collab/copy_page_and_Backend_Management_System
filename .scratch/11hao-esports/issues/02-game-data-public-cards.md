# 02 — 建立游戏数据基础与前台游戏卡片

**What to build:** 建立 PostgreSQL 中的游戏、服务和网站配置基础数据，并让访客可以在响应式首页看到四个启用游戏卡片。

**Blocked by:** None — can start immediately

**Status:** ready-for-agent

- [ ] 建立 SQLAlchemy 模型、Alembic 迁移和 PostgreSQL 测试数据库配置
- [ ] 建立 `Game`、`GameService` 和单条 `SiteSetting` 数据关系
- [ ] 导入原神、崩坏·星穹铁道、绝区零、鸣潮及完整初始服务数据
- [ ] 将提供的四张游戏图片作为本地初始封面
- [ ] 提供只返回启用游戏和启用服务、按排序值升序返回的公开接口
- [ ] Next.js 首页调用公开接口并展示游戏名称、标签、简介、封面、服务标签和起始价格
- [ ] 页面在桌面、平板和手机宽度下可用
- [ ] API 测试覆盖迁移数据、公开筛选、排序和起始价格数据
- [ ] 前台测试覆盖四个游戏卡片及本地封面展示
