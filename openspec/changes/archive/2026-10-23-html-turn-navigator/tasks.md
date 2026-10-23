# Tasks

## 1. Distinct panels

- [x] 1.1 Paint User with the warm panel and gold edge, Agent with the cooler panel, and System and Context with the shared panel, in both themes, and verify a render test that the dark and light pages use different User and Agent backgrounds, that a System or Context section uses neither, and that the pages still contain `#161616` or `#f7f7f4` for the chosen theme.

## 2. User-turn navigator

- [x] 2.1 Add the sticky navigator of fragment links to User sections, with the turn time and the first query line, an ellipsis clip, `Image` or `User` when the query is empty, a marked `:target` section, and no entries when there is no User section, and verify a render test that two User sections are linked, an Agent section is not, the later query lines are omitted from the entry, the stylesheet is sticky and clips with an ellipsis, and the page contains no script and no external address.
- [x] 2.2 Document the turn list in the README, and verify the README says the HTML page lists user turns and each entry jumps to that turn.

## Workflow follow-up

- Archive this change after review. The delta only adds requirements, so it can merge into the existing `session-export` spec.
