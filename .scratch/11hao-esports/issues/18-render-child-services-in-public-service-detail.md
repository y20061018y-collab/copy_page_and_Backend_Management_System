# 18 - Render Child Services In Public Service Detail

**What to build:** Render the approved child service list in the public service detail experience while preserving the existing `GameService` detail behavior.

**Blocked by:** 17 - Add Child Service Data And Read Contract, plus human approval of the 17 migration checkpoint report.

**Status:** DONE

- [x] Extend the existing public `GameService` detail view rather than introducing a new route.
- [x] Keep the selected `GameService` cover, name, description, and direct price visible according to the already approved public detail behavior.
- [x] Render child services sorted by sort order.
- [x] Each child service row/card shows child service name, description, and a right-side price badge.
- [x] When a child service image path is present, render the image at 16:9 with object-fit cover.
- [x] When a child service image path is absent, render a pure text child service item with no empty image placeholder, no broken image, and no reserved media gap.
- [x] Empty child service lists do not break the existing service detail view.
- [x] At 375px through 600px, the child service list follows the 14 mobile contract and remains usable in the approved two-column public layout.
- [x] Below 375px, including 374px, the child service list follows the 14 mobile contract and stacks into one column.
- [x] At narrow widths, the price badge must not be squeezed into unreadable wrapping and must not overlap the child service name or description.
- [x] Desktop public layout remains unchanged except for the directly necessary child service list addition.
- [x] Frontend tests cover rendering with images, rendering without images, sort order, empty child service lists, 600px two-column behavior, 374px one-column behavior, and narrow-screen price badge readability.
