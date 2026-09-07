# 14 — Apply Approved Mobile Layout Without Desktop Drift

**What to build:** Apply the approved public mobile catalog layout while keeping desktop public layout stable. Normal phone widths should use the approved two-column game-and-demand layout, and very narrow widths should stack to prevent collapsed text and controls.

**Blocked by:** 12 — Repair Public Service Catalog Experience.

**Status:** DONE

- [x] The public catalog uses the approved two-column layout from 375px through 600px.
- [x] The public catalog stacks into one column below 375px.
- [x] Game names, service names, prices, and buttons remain readable without incoherent overlap at supported mobile widths.
- [x] Desktop public layout remains unchanged except for directly necessary bug fixes.
- [x] Tests or visual checks cover the approved mobile breakpoint contract.
- [x] Any test that asserts side-by-side panels at every viewport width is removed or corrected.
