# 对齐服务目录与已批准规格

**Status:** DONE  
**Type:** corrective specification  
**Priority:** high  
**Labels:** `ready-for-agent`

## Problem Statement

当前分支在实现移动端目录和服务数量限制时，引入了未在已批准规格中定义的嵌套服务结构，并将价格从 `GameService` 迁移到新的额外模型。这导致数据库模型、公开 API、后台编辑体验、前台价格弹窗和领域文档出现不一致。

客户需要的是已批准规格中的 `Game` 与 `GameService` 服务目录：每个启用游戏最多展示五个启用服务，每个服务直接包含价格文本。管理员已有或将来维护的服务价格不能在迁移中丢失，前台价格弹窗应展示所选游戏的启用服务价格，而不是新的额外模型。

## Scope

本规范覆盖服务目录纠偏、服务价格恢复、未批准嵌套服务能力移除、移动端目录布局修正、显式封面保存流程修正，以及相关测试更新。

本规范以现有最高层 seam 验证行为：后端 FastAPI API 测试、Alembic 迁移测试、前端公共页面/后台页面行为测试、TypeScript 检查和生产构建。

## Solution

将实现重新对齐到已批准的电竞展示与管理系统规格。`GameService` 继续作为服务和价格条目，服务价格保存在 `GameService.price` 中。每个 `Game` 最多允许五个启用 `GameService`，禁用服务记录必须保留且不计入启用容量。

移除未批准的嵌套服务概念和对应 API。前台保留左侧游戏列表、右侧最多五个启用服务需求卡片的移动端体验；点击服务后，价格弹窗展示该游戏全部启用服务，供访客查看完整报价。后台继续在游戏编辑页维护服务名称、价格、说明、排序和启用状态。

移动端目录布局按已批准计划执行：宽度 375px 到 600px 使用左右两列目录和需求布局，宽度低于 375px 时改为单列堆叠。桌面端公共布局除必要回归修复外保持原状。

游戏封面选择应先本地预览，只有管理员点击显式保存后才关联到游戏记录。新封面保存成功前，旧封面继续有效。

## User Stories

1. As a website visitor, I want each service to show its own price directly, so that I can compare services without understanding nested project structures.
2. As a website visitor, I want the service price dialog to show all enabled services for the selected game, so that I can inspect the full price list in one place.
3. As a website visitor, I want disabled services hidden from the public catalog and price dialog, so that only currently available offers appear.
4. As a mobile visitor, I want the game list and service demand list to remain usable side by side on normal phone widths, so that I can switch games without losing context.
5. As a very narrow mobile visitor, I want the catalog columns to stack, so that text and buttons do not collapse or overflow.
6. As a desktop visitor, I want the existing public homepage layout to remain stable, so that a mobile-specific change does not alter the approved desktop presentation.
7. As an administrator, I want to create a service with a price text, so that new service offers can be maintained without code changes.
8. As an administrator, I want to edit a service price text, so that per-task, per-hour, per-star, and negotiable pricing remains supported.
9. As an administrator, I want to enable a disabled service only when the game has fewer than five enabled services, so that the public catalog respects the approved service cap.
10. As an administrator, I want to keep disabled services in the database, so that temporary hiding does not destroy service configuration.
11. As an administrator, I want a clear conflict error when attempting to create or enable a sixth service, so that I know why the save failed.
12. As an administrator, I want existing service prices preserved during deployment migrations, so that previously edited business data is not lost.
13. As an administrator, I want to choose a game cover and preview it before saving, so that accidental file selection does not immediately change public content.
14. As an administrator, I want old covers to remain associated until an explicit save succeeds, so that failed uploads or abandoned edits do not change the site.
15. As a maintainer, I want the domain glossary and implementation to agree on `GameService`, so that future agents and developers do not build against conflicting concepts.
16. As a maintainer, I want the public and admin API shape to match the accepted contract, so that deployed clients are not forced onto an unapproved nested service model.
17. As a maintainer, I want migration history to have a single valid Alembic head, so that upgrades can run predictably.
18. As a maintainer, I want tests to assert observable service catalog behavior, so that implementation details can change without weakening product guarantees.

## Implementation Decisions

- `GameService` remains the domain object for a service offer and directly owns the service price text.
- Service prices remain strings to support flexible Chinese price formats such as fixed price, per-star price, per-hour price, and negotiable price.
- The service cap applies to enabled `GameService` records per `Game`; disabled records are preserved and do not count toward the cap.
- Attempts to create, update, or enable a sixth active service return a structured conflict error with a stable code, human-readable Chinese message, and details object.
- The unapproved nested service model is removed from the active domain contract unless a future approved specification explicitly introduces it.
- Public game responses return enabled games and enabled services ordered by configured sort order.
- The public service dialog uses the selected game as the scope for the price list and displays all enabled services for that game.
- The public demand list displays at most five enabled services because the backend enforces the same enabled-service capacity.
- Admin service editing includes service name, price text, description, sort order, and enabled state.
- Admin service add/edit/enable flows surface service-cap conflicts instead of silently failing or using a generic error.
- Alembic migration changes must preserve existing administrator-edited service price data.
- If a migration that removes service prices has not been deployed, remove it from this branch. If it has been deployed anywhere shared, restore service prices with a forward migration.
- Migration history must resolve to a single current head after the repair.
- Public desktop layout changes unrelated to the mobile catalog plan are reverted unless separately approved.
- Mobile layout uses the approved two-column proportions from 375px through 600px and stacks below 375px.
- File selection for game covers updates local preview state only. The persistent game record changes only after an explicit save succeeds.
- Terminology in code-facing tests, domain docs, and user-visible admin copy should use the approved `Game`, `GameService`, and service wording consistently.

## Testing Decisions

- Backend behavior is tested through FastAPI HTTP/API tests wherever possible because the API is the highest stable seam for catalog rules.
- Migration behavior is tested through focused Alembic migration tests that verify price preservation, single-head migration history, and no accidental deletion of business data.
- Catalog domain tests may cover service-cap enforcement where HTTP setup would obscure the specific rule being verified.
- Frontend behavior is tested through existing public homepage and admin page tests, with assertions focused on rendered behavior and stable responsive requirements.
- Tests should not assert internal component names, private helper names, or arbitrary CSS implementation details unless the CSS rule is itself the approved behavior.
- Tests should cover creating a sixth enabled service, enabling a disabled sixth service, updating a disabled service to enabled as the sixth service, and preserving disabled records.
- Tests should cover seeded games exposing five enabled services with direct price text on each service.
- Tests should cover the public modal showing all enabled services for the selected game.
- Tests should cover the mobile breakpoint contract: two columns from 375px to 600px and stacked layout below 375px.
- Tests should cover game cover preview state and explicit save behavior at the highest practical frontend seam.
- Full verification includes backend tests, frontend tests, TypeScript checking, and production build.

## Acceptance Criteria

- `GameService` has a direct `price` field in the model, schemas, seed data, public response, and admin write flow.
- No active public or admin API requires nested services to manage or display prices.
- Existing administrator-edited service prices are not overwritten or dropped by migrations.
- Creating a sixth enabled service for a game returns a structured `409` conflict.
- Enabling or updating a disabled service to become the sixth enabled service returns the same structured conflict.
- Disabled services remain stored and can be re-enabled when capacity allows.
- Public `/api/games` returns only enabled games and enabled services in configured order.
- The public homepage demand list shows at most five enabled services for the selected game.
- The public price dialog shows the selected game's enabled services with price text.
- The mobile catalog uses the approved two-column layout from 375px through 600px.
- The mobile catalog stacks below 375px.
- Desktop public layout is unchanged except for directly necessary bug fixes.
- Choosing a game cover previews locally and does not persist until the explicit game save action succeeds.
- Tests and type/build checks pass after the repair.

## Out of Scope

- Introducing a new nested service model, package model, or SKU model.
- Redesigning the public desktop homepage.
- Adding permanent delete behavior for games, services, covers, or uploaded files.
- Changing authentication, administrator roles, order/payment features, analytics, search, localization, object storage, or backup strategy.
- Reworking the full admin UI architecture beyond the changes needed to restore approved service editing behavior.

## Blockers

- If the product owner actually wants nested service variants, the approved specification and domain glossary must be updated before implementation continues.
- If the service-price-removal migration has already been applied to a shared or production database, repair must use a forward migration rather than deleting migration history.

## Further Notes

This is a corrective spec for the current branch review. It assumes the original电竞展示与管理系统 specification remains the source of truth and that the mobile catalog/service-cap plan is limited to five enabled `GameService` records per `Game`, not a new nested price model.
