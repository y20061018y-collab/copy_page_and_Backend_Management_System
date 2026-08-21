# 11号电竞展示与管理系统

**Status:** ready-for-agent  
**Type:** feature specification  
**Priority:** high  
**Labels:** `ready-for-agent`  

## Problem Statement

客户需要一套可以正式部署并交付源码的电竞服务展示系统。现有内容是一个单文件网页原型，价格使用浏览器本地存储，无法由客户通过后台维护，也不适合正式服务器部署。客户需要同时支持桌面端、移动端和后台管理，并允许后续购买域名与服务器后部署。

## Solution

构建一套 Next.js 15 + TypeScript 前台和后台、FastAPI API、PostgreSQL 数据库的可部署系统。前台展示四个游戏及服务价格，后台通过管理员登录维护游戏、服务、排序、启用状态、联系方式、游戏封面和工作室图片。项目使用 Alembic、Docker Compose、Nginx 和部署文档交付。

## User Stories

1. As a website visitor, I want to see the 11号电竞 brand and subtitle, so that I understand the studio and its service positioning.
2. As a website visitor, I want the public page to work on desktop, tablet, and mobile, so that I can browse services from any device.
3. As a website visitor, I want to see enabled games ordered by their configured priority, so that the most important games appear first.
4. As a website visitor, I want to see a game cover, name, tag, description, service tags, and starting price, so that I can quickly compare available games.
5. As a website visitor, I want to open a game service price dialog, so that I can inspect all enabled services without leaving the homepage.
6. As a website visitor, I want the price dialog to scroll on small screens, so that long service lists remain usable on mobile.
7. As a website visitor, I want to close the price dialog with a button, backdrop, or Escape key, so that I can return to browsing naturally.
8. As a website visitor, I want disabled games and services hidden from public pages, so that I only see currently offered services.
9. As a website visitor, I want to open a contact dialog from the consultation button, so that I can find a way to contact the studio.
10. As a website visitor, I want to copy configured WeChat, QQ, and phone values, so that I can contact the studio conveniently.
11. As a mobile visitor, I want to tap the configured phone number to dial, so that I do not need to copy it manually.
12. As a website visitor, I want unconfigured contact fields hidden, so that placeholder values are not mistaken for real contact information.
13. As an administrator, I want to log in with a protected account, so that anonymous visitors cannot change public content.
14. As an administrator, I want an overview dashboard, so that I can quickly see game and service counts and recent activity.
15. As an administrator, I want to list games filtered by all, enabled, or disabled state, so that I can find content to maintain.
16. As an administrator, I want to create a game, so that I can add a supported game without code changes.
17. As an administrator, I want to edit a game's name, slug, tag, description, colors, cover, order, and enabled state, so that the public card stays accurate.
18. As an administrator, I want to enable or disable a game with confirmation, so that I can control public availability without destroying data.
19. As an administrator, I want to reorder games, so that the public page follows the desired business priority.
20. As an administrator, I want to add a service to a game, so that I can expand the price list.
21. As an administrator, I want to edit a service name, price text, description, order, and enabled state, so that different pricing formats such as per-star, per-hour, and negotiable prices are supported.
22. As an administrator, I want to enable or disable a service with confirmation, so that I can temporarily hide an offer without losing its data.
23. As an administrator, I want to reorder services, so that related or important services appear in the intended order.
24. As an administrator, I want unsaved changes clearly indicated, so that I do not leave the page believing changes were stored.
25. As an administrator, I want to preview a selected game cover before saving, so that I can verify the image.
26. As an administrator, I want to upload and replace a game cover, so that public branding can be maintained without source changes.
27. As an administrator, I want to preview and replace the studio image from settings, so that the public brand image can be updated without developer assistance.
28. As an administrator, I want a saved studio image to appear in the public brand area and footer, so that the updated identity is visible to visitors.
29. As an administrator, I want to edit the site name, subtitle, contact values, and contact instructions, so that common content can be maintained from the backend.
30. As an administrator, I want invalid image types and oversized uploads rejected, so that the server remains safe and predictable.
31. As an administrator, I want login state to use an HttpOnly cookie, so that the authentication token is not exposed to browser scripts.
32. As an administrator, I want disabled records retained, so that accidental disabling does not destroy historical configuration.
33. As a maintainer, I want database schema changes managed by Alembic, so that deployments can upgrade safely.
34. As a maintainer, I want four games and their complete initial services seeded, so that the delivered site is usable immediately.
35. As a client, I want the project to run with Docker Compose, so that I can deploy it to a purchased Linux server.
36. As a client, I want deployment, environment, backup, and restore instructions, so that another developer can operate the delivered source.
37. As a client, I want PostgreSQL and upload files persisted through volumes, so that container restarts do not lose business data or images.

## Implementation Decisions

- Build one Next.js 15 App Router application containing both public routes and `/admin` routes.
- Build one FastAPI application exposing public, authentication, and authenticated admin API groups.
- Use PostgreSQL as the source of truth with SQLAlchemy 2 models and Alembic migrations.
- Use `AdminUser`, `Game`, `GameService`, and single-record `SiteSetting` models. `Game` has a one-to-many relationship with `GameService`; `SiteSetting` contains `studio_image`.
- Keep prices as text rather than numeric values to support `¥ 30`, `¥ 20/星`, `¥ 25/时`, and `¥ 面议`.
- Use enabled state instead of permanent deletion for games and services.
- Use JWT in an HttpOnly cookie with a seven-day default lifetime, Secure in production, configured SameSite behavior, and no public registration.
- Expose public read endpoints that return only enabled games and services ordered by `sort_order`.
- Keep game, service, reorder, settings, and upload operations as separate API actions rather than one aggregate save endpoint.
- Support game cover uploads and studio image uploads. Accept JPG, JPEG, PNG, and WEBP up to 5 MB; validate extension and MIME type; generate server-side filenames; persist files under separate game and studio upload directories; store relative paths in the database.
- Use the existing four game images as initial local assets and `图片/工作室图标.jpg` as the initial studio image.
- Provide desktop sidebar navigation and mobile drawer navigation in the admin UI; switch admin tables to cards on narrow screens.
- Use a dark esports visual language based on the existing prototype, with responsive layout, moderate motion, and reduced-motion support.
- Return structured API errors with `code`, `message`, and `details`, using standard HTTP statuses for validation, authentication, conflicts, missing resources, upload size, and server errors.
- Deploy with Docker Compose, PostgreSQL volumes, upload volumes, and an Nginx reverse-proxy example for `/`, `/admin`, and `/api`.
- Provide seed commands for the initial four games, complete service data, default settings, and administrator creation from environment variables.

## Testing Decisions

- Test external behavior at the highest available seams rather than internal implementation details.
- Use FastAPI HTTP/API tests as the backend seam. Cover migrations or test database setup, authentication, public filtering, game and service CRUD, enable/disable behavior, ordering, settings, image validation, studio image replacement, and structured errors.
- Use browser-level end-to-end tests as the frontend seam. Cover the public homepage, responsive service dialog, contact dialog, admin login, dashboard, game editing, service editing, studio image upload, save, refresh, and public visibility.
- Add focused frontend unit tests only for stable pure behavior such as price extraction, enabled filtering, ordering, form validation, and API response mapping.
- Tests must assert observable results and persisted behavior, not CSS implementation, component names, or SQLAlchemy internals.
- Because the repository currently has no prior application tests, establish the API test harness and browser test harness as the initial testing infrastructure rather than copying existing patterns.

## Out of Scope

- Public user accounts, multi-role permissions, orders, payments, carts, coupons, balances, online support, chat, comments, ratings, notifications, analytics, complex reports, search, localization, object storage, automatic cloud backup, SMS, email, WeChat public accounts, and mini-programs.
- Permanent deletion of games, services, or images.
- Multi-image galleries or a separate media library model.
- Automatic cloud backup and disaster recovery.

## Further Notes

- The current repository contains no application code, remote repository, issue tracker configuration, tests, or commits. It currently contains the five provided image assets and the design specification.
- The highest test seams are the FastAPI HTTP API and browser user flows; this is intentional because the system is a new full-stack application.
- Initial server assumptions are Ubuntu 22.04/24.04, at least 2 CPU cores, 4 GB RAM, 40 GB disk, Docker, Docker Compose, and Git.
- The source-code handoff must include frontend and backend source, migrations, seed data, Docker and Nginx configuration, `.env.example`, README, deployment instructions, and database/upload backup instructions.
