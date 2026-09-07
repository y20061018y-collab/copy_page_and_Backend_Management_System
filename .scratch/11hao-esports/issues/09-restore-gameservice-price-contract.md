# 09 — Restore `GameService` Price Contract

**What to build:** Restore the approved service price contract so each `GameService` directly owns a price text again. Existing administrator-edited service prices must survive schema changes, public API responses must expose direct service prices, and admin writes must accept and persist direct service prices.

**Blocked by:** None — can start immediately.

**Status:** DONE

- [x] `GameService` directly stores a non-empty price text suitable for fixed, per-star, per-hour, and negotiable pricing formats.
- [x] Public game responses include direct service price text on enabled services.
- [x] Admin service create and update requests accept direct service price text.
- [x] Seeded games expose five enabled services per game, with direct price text on each service.
- [x] Existing administrator-edited service prices are preserved through migration; migration-before and migration-after price data diff is zero, or matches an explicitly documented expected mapping.
- [x] Alembic migration history is written against a single head from the start.
- [x] Alembic upgrade and downgrade paths both run successfully for this contract change.
- [x] Tests cover price preservation, public price exposure, admin price persistence, and migration graph validity.
