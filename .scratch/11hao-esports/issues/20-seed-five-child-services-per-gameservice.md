# 20 - Seed Five Child Services Per GameService

**What to build:** Add acceptance seed data so every existing seeded `GameService` has five child services with sample names, descriptions, prices, order, and selective example images.

**Blocked by:** 17 - Add Child Service Data And Read Contract, plus human approval of the 17 migration checkpoint report.

**Status:** DONE

- [x] Seed exactly five child services for each existing seeded `GameService` across the current four games and their services.
- [x] Use realistic short child service names, descriptions, and price text suitable for direct public acceptance testing.
- [x] Preserve existing seeded games, `GameService` rows, direct `GameService.price` values, sort order, and enabled state.
- [x] Most seeded child services should have a null image path so the pure text layout is visible during acceptance.
- [x] Select 2-3 games and, for one `GameService` in each selected game, assign existing asset-space image paths to 1-2 child services as example child service images.
- [x] Reuse only images that already exist in the project's asset/upload/static space; do not download, generate, or add new image assets for seed examples.
- [x] Ensure public acceptance data makes both layouts immediately visible: child service items with images and child service items with no image.
- [x] Seed behavior is repeatable in the test environment and does not duplicate child service rows across repeated setup runs.
- [x] Tests cover seeded child service count, parent ownership, sorted order, price text, selective image paths, null image paths, and preservation of existing `GameService` seed data.
