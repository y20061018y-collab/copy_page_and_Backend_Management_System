# 16 - Approved Child Service Spec

**What to build:** Publish the approved "子服务" feature specification for `GameService`. This ticket is the source of truth for scope, terminology, release order, and non-goals before implementation tickets begin.

**Blocked by:** None.

**Status:** DONE

- [x] Terminology is fixed: user-facing copy uses "子服务"; code-facing names use `ChildService` or `child_services` where an English identifier is required.
- [x] This is a brand-new approved feature. Implementation must not restore deleted model code, deleted migration logic, deleted UI behavior, or deleted terminology from repository history.
- [x] Each `GameService` may own multiple child service rows with name, description, price text, sort order, and optional image path.
- [x] Child service count is configurable through normal administrator create, update, delete, and reorder operations. Seed data should provide the default acceptance shape of five child services per `GameService`; the product does not require automatic blank rows or a global count setting.
- [x] `GameService.price` remains a direct, non-empty price text and the 09 price contract must not regress.
- [x] The migration path must preserve the 0007 legacy compatibility behavior and keep Alembic at a single head.
- [x] Child service image guidance is fixed for this release: "子服务配图（可选）。建议尺寸：1200 × 675 px（16:9），支持 JPG、PNG、WebP，最大 5 MB。"
- [x] Public detail pages render child services as a list under the selected `GameService`: optional image when present, no image placeholder when absent, child service name, short description, and a right-side price badge.
- [x] Administrators can manage child services for each `GameService`, including optional image upload through the existing asset upload capability.
- [x] The release order is fixed: 17 completes and reports the database migration checkpoint first; only after approval should 18, 19, and 20 proceed; 21 performs final regression and terminology verification.
