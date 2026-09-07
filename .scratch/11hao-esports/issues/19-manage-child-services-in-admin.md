# 19 - Manage Child Services In Admin

**What to build:** Add administrator create, update, delete, reorder, and optional image management for child services under each `GameService`.

**Blocked by:** 17 - Add Child Service Data And Read Contract, plus human approval of the 17 migration checkpoint report.

**Status:** DONE

- [x] Add authenticated admin API support for creating, updating, deleting, and reordering child services under a `GameService`.
- [x] Validate required child service fields: name, description, price text, and sort order.
- [x] Accept an optional child service image path and persist null or empty image state without error.
- [x] Reuse the existing asset upload capability for child service images, including existing file type and size constraints where applicable.
- [x] Do not require an upload request when the administrator leaves the child service image blank.
- [x] Add a clear/remove image path control if the local admin editing pattern supports it without broad refactoring.
- [x] Add child service management UI inside the existing admin `GameService` editing workflow.
- [x] The image upload control copy must read: "子服务配图（可选）。建议尺寸：1200 × 675 px（16:9），支持 JPG、PNG、WebP，最大 5 MB。"
- [x] Saving a child service with no image succeeds and the public page later renders it as a pure text item.
- [x] Deleting a child service removes the row from the parent `GameService`; physical deletion of uploaded asset files is out of scope.
- [x] Existing admin `GameService` create, update, cover upload, enabled state, and maximum enabled service behavior from 09-15 remain unchanged.
- [x] Backend tests cover admin create, update, delete, reorder, optional image, and no-image save behavior.
- [x] Frontend tests cover admin editing controls, image upload copy, optional image save behavior, and no regressions to existing service editing.
