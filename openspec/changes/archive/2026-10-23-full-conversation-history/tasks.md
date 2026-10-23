# Tasks

## 1. Checkpoint messages

- [x] 1.1 Read a protobuf root's field 1 as the live role messages and expand checkpoint blobs listed elsewhere in that root, and verify a synthetic store test that earlier checkpoint messages come before the live tail, a message id repeated by a second checkpoint appears once in the earlier position, and the checkpoint's summary text is not a turn.
- [x] 1.2 Keep a raw hash-list root in its existing order, and verify `test_messages_stay_in_order_without_checkpoint_duplicate` still returns each message once and does not treat the repeat checkpoint as skipped.

## 2. Footer

- [x] 2.1 Leave checkpoints, file bodies, and labels out of the skipped-data footer, and verify a synthetic store test that a checkpoint id and a file body referenced by the root are absent from the footer while a transcript child that is not a message, checkpoint, or image is still named.

## Workflow follow-up

- Archive `export-agent-sessions` before this change so the unrecognized-data requirement exists to be modified.
- Archive `full-conversation-history` after review.
