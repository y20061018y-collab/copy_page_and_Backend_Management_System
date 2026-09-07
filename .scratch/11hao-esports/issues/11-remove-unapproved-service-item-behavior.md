# 11 — Remove Unapproved Service Item Behavior

**What to build:** Remove the unapproved nested service behavior from the active product contract. The system should no longer require, expose, or maintain nested services to represent service prices; `GameService` is the only service-price unit.

**Blocked by:** 09 — Restore `GameService` Price Contract.

**Status:** DONE

- [x] Public API consumers do not need service child records to display prices.
- [x] Admin API consumers do not need service child records to create or edit prices.
- [x] Service item specific create, update, enable, disable, reorder, and public display behavior is removed from active flows.
- [x] Any migration repair preserves existing service price data before removing unapproved nested behavior.
- [x] Tests no longer assert nested service behavior as required product behavior.
- [x] Domain-facing code and tests use `GameService` as the service price concept.
