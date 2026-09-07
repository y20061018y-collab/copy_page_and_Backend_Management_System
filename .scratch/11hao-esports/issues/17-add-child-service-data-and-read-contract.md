# 17 - Add Child Service Data And Read Contract

**What to build:** Add the new child service data model and read contract under `GameService`, with a new Alembic migration based on the current single head.

**Blocked by:** 16 - Approved Child Service Spec.

**Status:** DONE

**Human checkpoint:** Stop after this ticket is implemented and verified. Report the migration shape, upgrade/downgrade result, single-head status, and test result for human review before any of 18, 19, or 20 starts.

- [x] Add a new `ChildService` model/table related to `GameService`.
- [x] Store child service name, description, price text, sort order, and nullable image path.
- [x] Define ownership from `GameService` to child services using the repository's existing ORM relationship style, including appropriate cascade behavior when a parent `GameService` is removed.
- [x] Expose sorted `child_services` data on public and admin read responses without changing existing `GameService` direct price behavior.
- [x] Keep child service price as flexible text, matching the existing direct service price contract style.
- [x] Create a new Alembic migration from the current 0007 head; do not branch migration history.
- [x] The migration creates only the new child service structure and must not copy, restore, or depend on deleted nested implementation data or repository history.
- [x] Alembic upgrade and downgrade both run successfully.
- [x] `alembic heads` reports exactly one head after the migration is added.
- [x] Existing 09 price contract tests and 0007 legacy compatibility tests continue to pass unchanged.
- [x] Backend tests cover model persistence, parent ownership, sorted reads, nullable image path, public read shape, admin read shape, migration graph validity, upgrade, and downgrade.
- [x] Stop after verification and report this checkpoint before starting downstream tickets.
