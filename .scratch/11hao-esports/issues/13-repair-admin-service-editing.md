# 13 — Repair Admin Service Editing

**What to build:** Repair admin service maintenance around the approved `GameService` model. Administrators should be able to create, edit, reorder, enable, and disable services with direct price text, and should receive a structured conflict when trying to exceed five enabled services for one game.

**Blocked by:** 09 — Restore `GameService` Price Contract; 11 — Remove Unapproved Service Item Behavior.

**Status:** DONE

- [x] This ticket can run in parallel with ticket 12 after ticket 09 is complete, once ticket 11 is also complete for the admin surface.
- [x] The admin game editor supports service name, price text, description, sort order, and enabled state.
- [x] Creating an enabled sixth service for a game returns a structured conflict response.
- [x] Enabling a disabled service as the sixth enabled service returns the same structured conflict response.
- [x] Updating a disabled service to enabled as the sixth enabled service returns the same structured conflict response.
- [x] Disabled services remain stored and can be re-enabled when capacity allows.
- [x] Admin UI surfaces the service-cap conflict clearly instead of showing a generic failure.
- [x] Tests cover create, update, enable, disable, reorder, and service-cap conflict behavior.
