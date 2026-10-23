# Proposal

## Why

The latest export of this chat shows only the newest turns and a long footer of "Skipped unrecognized data". The older turns are in the store. The reader treats the blobs that point at them as unknown data, so the history never reaches the page.

## What Changes

- Include role messages listed inside checkpoint blobs the root references, in conversation order, before the later turns that are not in those checkpoints. A message id appears once.
- **BREAKING**: A checkpoint blob is not named as skipped data once its messages are included. File bodies, labels, and other side blobs that are not transcript turns are not named in the footer either.
- A transcript child that is still not a message, a checkpoint, or an image keeps a short footer line. The raw hash-list root used by the tests keeps its current order, and a checkpoint that only repeats those message ids still does not duplicate them.
- The store stays read-only. Checkpoint summary text stored beside the message list is not a separate turn.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `session-export`: The transcript includes checkpoint history, and the unrecognized-data footer no longer lists checkpoints or side blobs. The main spec is not in `openspec/specs/` yet. Archive `export-agent-sessions` before this change.

## Impact

- `session_export/store.py`: read an ordered transcript from the root, and expand checkpoint blobs whose message ids are 32-byte digests. Stop treating every embedded digest as a transcript child.
- Tests that build a synthetic store. Add a fixture whose older messages live only in a checkpoint, and one whose root also references a file body that must not appear in the footer.
- No new flags and no new dependencies.
