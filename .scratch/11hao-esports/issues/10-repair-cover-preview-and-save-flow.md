# 10 — Repair Cover Preview And Save Flow

**What to build:** Make cover selection a preview-only action until the administrator explicitly saves. Selecting a new game cover should update the local preview, while the currently saved public cover remains unchanged until the save action succeeds.

**Blocked by:** None — can start immediately.

**Status:** DONE

- [x] Choosing a game cover file updates the admin page preview without immediately changing the persisted game record.
- [x] The saved game cover changes only after the administrator explicitly saves the game.
- [x] If upload or save fails, the previously saved cover remains associated with the game.
- [x] Leaving or abandoning an unsaved cover selection does not change public content.
- [x] The admin page clearly communicates save success or failure for cover changes.
- [x] Tests cover preview-before-save behavior and persistence only after explicit save.
