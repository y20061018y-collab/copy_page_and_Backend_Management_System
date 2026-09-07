# 21 - Child Service Final Regression And Terminology

**What to build:** Complete the child service release with full regression verification, terminology cleanup, and release evidence after 18, 19, and 20 are complete.

**Blocked by:** 18 - Render Child Services In Public Service Detail; 19 - Manage Child Services In Admin; 20 - Seed Five Child Services Per GameService.

**Status:** DONE

- [x] Update `CONTEXT.md` with the approved child service domain term, ownership relationship, and optional image behavior.
- [x] Verify user-facing Chinese copy consistently uses "子服务" for this feature.
- [x] Verify new code-facing identifiers consistently use `ChildService`, `childService`, or `child_services` as appropriate.
- [x] Verify no new active model, API, UI, or migration code restores deleted nested implementation terminology or behavior.
- [x] Preserve all accepted behavior from tickets 09-15, including direct `GameService.price`, cover preview/save behavior, public service detail behavior, admin service editing, and mobile layout breakpoints.
- [x] Run the full backend test suite. The baseline is 29 passed before this feature; the final count must only increase or remain compatible with added tests, with no failures.
- [x] Run the full frontend test suite. The baseline is 21 passed before this feature; the final count must only increase or remain compatible with added tests, with no failures.
- [x] Run TypeScript checking and production build verification.
- [x] Verify Alembic still has exactly one head.
- [x] Verify Alembic upgrade and downgrade paths for the child service migration.
- [x] Verify public acceptance data displays both child service image layout and pure text child service layout.
- [x] Final report includes backend test result, frontend test result, type/build result, Alembic single-head result, migration upgrade/downgrade result, and any residual risk.
