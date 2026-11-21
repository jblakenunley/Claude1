# Salesforce

Vendor-perspective advisor: how would Salesforce Inc. proceed? The counterpart
to Snowflake on any platform or Salesforce-integration decision. No platform
commitment.

| File | Purpose |
|---|---|
| `../.claude/agents/salesforce.md` | Agent definition (Claude Code subagent), including the panel protocol |
| `DOCTRINE.md` | Salesforce's published architect guidance, distilled; review protocol; known gaps |
| `LEARNING_PATH.md` | 30-day daily curriculum, run against real systems |
| `LEARNING_LOG.md` | Dated findings, one per lesson |
| `progress.json` | Where the path stands |

## Use

In Claude Code from this repo:

- `Ask salesforce: <question>` — Salesforce's best case, plus when it isn't the answer and what Salesforce gains
- `Run the platform panel on <question>` — snowflake and salesforce answer the same brief; the main session compares; Blake decides
- `Have salesforce run today's lesson` — advances the path one day and commits

## Source

Doctrine distilled from Salesforce's published architect guidance
(Well-Architected, Integration Patterns, decision guides), read 2026-11-21.
The agent shares the name only.
