# Spec Delta

## ADDED Requirements

### Requirement: Navigator time format
A parsed navigator turn time SHALL be written as YY-MM-DD hh:mm with a two-digit year, zero-padded month and day, and a 24-hour clock. An unparsed turn time SHALL stay as stored. User and Agent headings SHALL keep their existing turn time.

#### Scenario: Afternoon becomes 24-hour
- **WHEN** a User section's turn time is `Oct 23, 2026 01:08 PM`
- **THEN** the navigator shows `26-10-23 13:08`

#### Scenario: Morning stays in the morning
- **WHEN** a User section's turn time is `Oct 23, 2026 11:13 AM`
- **THEN** the navigator shows `26-10-23 11:13`

#### Scenario: Single-digit day is zero-padded
- **WHEN** a User section's turn time is `Sep 1, 2026 09:05 AM`
- **THEN** the navigator shows `26-09-01 09:05`

#### Scenario: Midnight is zero hour
- **WHEN** a User section's turn time is `Oct 23, 2026 12:00 AM`
- **THEN** the navigator shows `26-10-23 00:00`

#### Scenario: Noon stays at twelve
- **WHEN** a User section's turn time is `Oct 23, 2026 12:00 PM`
- **THEN** the navigator shows `26-10-23 12:00`

#### Scenario: Unparsed time stays as stored
- **WHEN** a User section's turn time cannot be parsed
- **THEN** the navigator shows that text as stored

#### Scenario: Heading keeps the catalog time
- **WHEN** the same turn appears in a User heading and in the navigator
- **THEN** the heading keeps the catalog time and the navigator shows the compact time

### Requirement: Navigator time size
A navigator turn time SHALL use a smaller font than the query text in that entry.

#### Scenario: Parsed time is smaller
- **WHEN** the navigator shows a parsed turn time beside a query
- **THEN** that time uses a smaller font than the query text

#### Scenario: Unparsed time is smaller
- **WHEN** the navigator shows an unparsed turn time beside a query
- **THEN** that time uses the same smaller font
