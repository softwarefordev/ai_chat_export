# Tasks

## 1. Wider stacked navigator

- [x] 1.1 Make the side-by-side navigator a 30rem column starting at 70rem, and verify a render test that the stylesheet uses `30rem` and `70rem` and no longer uses the `16rem` column or the `52rem` breakpoint.
- [x] 1.2 Stack the time above the prompt, set that time to 10px on one line, set the navigator to a sans-serif face, and keep the transcript in Georgia, and verify a render test that the time element precedes the prompt, the stylesheet sets `10px` and `nowrap` on the navigator time, the navigator is sans-serif, and the body face stays Georgia.

## Workflow follow-up

- Archive this change after review. The delta only adds requirements, so it can merge into the existing `session-export` spec.
