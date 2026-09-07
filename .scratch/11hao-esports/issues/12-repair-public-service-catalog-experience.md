# 12 — Repair Public Service Catalog Experience

**What to build:** Repair the public catalog so visitors see up to five enabled `GameService` demand cards for the selected game, and the price dialog shows that selected game's enabled service list with direct price text.

**Blocked by:** 09 — Restore `GameService` Price Contract.

**Status:** DONE

- [ ] This ticket can run in parallel with ticket 13 after ticket 09 is complete.
- [ ] The public game list shows only enabled games ordered by configured priority.
- [ ] The public demand list shows at most five enabled services for the selected game.
- [ ] Disabled services are hidden from public demand cards and price dialog rows.
- [ ] Clicking a service opens a price dialog scoped to the selected game.
- [ ] The price dialog displays all enabled services for the selected game with direct service price text.
- [ ] The price dialog remains closable by close button, backdrop, and Escape key.
- [ ] Tests cover the demand-card limit and the full selected-game service price dialog behavior.
