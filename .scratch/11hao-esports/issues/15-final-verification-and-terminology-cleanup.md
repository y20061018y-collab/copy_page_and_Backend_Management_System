# 15 — Final Verification And Terminology Cleanup

**What to build:** Clean up terminology and run final verification after the service catalog repair is complete. The codebase, tests, user-visible admin copy, and domain docs should consistently describe the approved `GameService` model and avoid unapproved nested service language.

**Blocked by:** 09 — Restore `GameService` Price Contract; 11 — Remove Unapproved Service Item Behavior; 12 — Repair Public Service Catalog Experience; 13 — Repair Admin Service Editing; 10 — Repair Cover Preview And Save Flow; 14 — Apply Approved Mobile Layout Without Desktop Drift.

**Status:** DONE

- [x] Replace legacy Chinese nested-service wording with “服务” or “服务报价” depending on context.
- [x] Replace legacy English nested-project wording with “services” or “service price rows” depending on context.
- [x] Replace legacy large-project wording with “服务” or `GameService` depending on whether the text is user-facing or code-facing.
- [x] Do not introduce a nested service model, package model, or SKU term unless a future approved spec adds that concept.
- [x] Domain docs, tests, and admin copy consistently align with `Game`, `GameService`, `Game catalog`, `Public Game catalog snapshot`, and `SiteSetting`.
- [x] Backend tests pass.
- [x] Frontend tests pass.
- [x] TypeScript checking passes.
- [x] Production build passes.
- [x] Alembic has a single valid head after all repair tickets are complete.
- [x] Final verification confirms public catalog, admin service editing, cover preview/save, and mobile layout behavior all match the corrective spec.
