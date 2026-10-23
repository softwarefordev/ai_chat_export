# Design

## Context

See proposal.md for why. `load_conversation` scans the root blob one byte at a time for any 32-byte digest that exists in the store. On this chat that scan returns the latest role messages and also two checkpoint blobs, file bodies, and short label blobs. Only direct JSON role messages become turns. Everything else is skipped, which is the long footer in `Agent Session Exporter.html`. The page shows the two latest User sections. The store's checkpoints list the earlier role messages: one list begins with an 11:13 AM user query, the next with a 12:27 PM user query. They share a single message id, at index 272 of the first list and index 0 of the second. The root's own message list does not include those earlier messages.

The root for that chat parses as protobuf. Field 1 is the ordered live role-message ids. Field 13 is the two checkpoint ids. Fields 3 and 8 are labels and file bodies. A checkpoint parses as protobuf too: field 1 is the ordered message ids, field 2 is summary text that starts with `<summary`, and field 4 is one related message id. The test stores are not protobuf. `write_db` concatenates raw 32-byte ids and appends a checkpoint that repeats those same ids.

## Goals / Non-Goals

**Goals:**

- Emit checkpoint role messages once, in checkpoint order, then the live messages that were not in a checkpoint.
- Leave the raw hash-list root and its repeat checkpoint behaving as they do now.
- Stop naming checkpoints, file bodies, and labels in the footer.

**Non-Goals:**

- Decrypting blobs. `blobEncryptionKey` stays unused.
- A new flag. The existing query, detail, and verbose filters still apply to the recovered messages.
- Reading `~/.cursor/chats` from tests.

## Decisions

### Take ids from protobuf fields, not a sliding scan

When the root parses as protobuf, the live transcript is field 1's 32-byte ids, in order. Checkpoint ids are the other id fields whose blobs are checkpoints. A sliding scan also matches hashes that sit inside file text and nested payloads, which is how this export gained dozens of skipped lines.

Alternative: keep the scan and classify each hit. The same digest can show up inside unrelated bytes, so the transcript order would still be wrong.

A root that does not parse as protobuf stays a concatenation of 32-byte ids, which is what `write_db` writes.

### A checkpoint is a message-id list

A checkpoint is either a raw concatenation of message ids, or a protobuf whose field 1 is 32-byte ids of role messages. Emit those role messages. Do not emit field 2. The `<summary` text is the checkpoint's own summary document, and the filtered transcript already has a separate rule for `conversation_summary` messages.

### Dedupe in listed order

Walk checkpoint ids in the order the root references them. Emit each field-1 role message that has not been emitted. Then emit live role messages that have not been emitted. On this chat that places the 11:13 AM list, then the 12:27 PM list, then the latest tail. The shared id appears once, in the earlier list. The four messages that follow the shared id in the earlier checkpoint stay, because they are stored turns. Cutting the earlier list at the fork would drop them.

A raw repeat checkpoint adds no new ids, so it does not duplicate messages and is not a footer line.

### Side blobs are not conversation data

Label blobs and file bodies referenced beside the transcript are not turns and are not skipped conversation data. A child of the transcript list that is not a role message, a checkpoint, or an image is still named in the footer. Unlinked images stay on the existing image rule.

## Risks / Trade-offs

- [The four messages after the shared id are a short fork, so they appear before the later checkpoint continues] → They are stored turns and the page shows them once. A later change can cut at the fork if that reads worse.
- [Another chat uses a different protobuf layout] → Only expand a blob when its id list actually points at role messages. Otherwise leave the existing footer behavior for a transcript child that still cannot be read.
- [Archiving this change before `export-agent-sessions` has no base requirement to modify] → Archive `export-agent-sessions` first.

## Migration Plan

No data migration. Re-export replaces the HTML. Rollback is the sliding scan that lists non-message children as skipped.

## Open Questions

None.
