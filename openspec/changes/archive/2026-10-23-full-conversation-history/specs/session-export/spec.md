# Spec Delta

## ADDED Requirements

### Requirement: Checkpoint history
The export SHALL include each role message listed by a checkpoint the root references. Messages SHALL follow that checkpoint's order. An earlier checkpoint SHALL come before a later one, and both SHALL come before transcript messages that are not in those checkpoints. A message id SHALL appear once.

#### Scenario: Earlier turns precede the latest tail
- **WHEN** the root lists only the latest turns and a checkpoint lists earlier role messages
- **THEN** the export includes those earlier messages before the latest turns

#### Scenario: Repeated message
- **WHEN** a later checkpoint repeats a message id already listed by an earlier checkpoint
- **THEN** that message appears once, in the earlier position

#### Scenario: Repeat index
- **WHEN** a checkpoint lists only message ids that the root already lists
- **THEN** those messages appear once, in the root's order

### Requirement: Checkpoint summary is not a turn
Summary text stored beside a checkpoint's message list SHALL NOT appear as its own turn.

#### Scenario: Summary field omitted
- **WHEN** a checkpoint stores summary text next to its message ids
- **THEN** the transcript includes the listed role messages and does not add a turn for that summary text

## MODIFIED Requirements

### Requirement: Unrecognized conversation data
The export SHALL include the turns the reader understands and SHALL name skipped conversation data in a short footer. A checkpoint whose messages were included, and a file body or label that is not a transcript turn, SHALL NOT be named as skipped conversation data.

#### Scenario: Unknown blob
- **WHEN** the conversation contains data the reader cannot interpret
- **THEN** the export includes the understood turns and a footer entry for the skipped data

#### Scenario: Checkpoint is not skipped
- **WHEN** a checkpoint's role messages are included in the transcript
- **THEN** the footer does not name that checkpoint blob

#### Scenario: Side blob is not skipped
- **WHEN** the root references a file body that is not a transcript turn
- **THEN** the footer does not name that file body
