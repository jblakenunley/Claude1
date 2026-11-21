# Snowflake

Architecture advisor for AI agent and data-agent systems in the 1+Claude stack.

| File | Purpose |
|---|---|
| `../.claude/agents/snowflake.md` | Agent definition (Claude Code subagent) |
| `DOCTRINE.md` | Best practices, review protocol, known gaps in the source |
| `LEARNING_PATH.md` | 30-day daily curriculum, run against real systems |
| `LEARNING_LOG.md` | Dated findings, one per lesson |
| `progress.json` | Where the path stands |
| `ORG.md` | Every agent, its layer and human anchor |
| `CONTRACTS.md` | Frozen interfaces between parts of the system, with owners |
| `REVIEW_QUEUE.md` | What agents may not change themselves, for review and decision |

## Use

In Claude Code from this repo:

- `Use snowflake to review <design or file>` — runs the §8 review protocol
- `Ask snowflake: <architecture question>` — guidance against the doctrine
- `Have snowflake work the review queue` — reviews open items against §8
- `Have snowflake run today's lesson` — advances the path one day and commits

A scheduled task runs the daily lesson automatically and pushes the log entry.

## Source

Doctrine distilled from *A Practical Guide to AI Agents* (Snowflake Inc.,
Dec 2025). The agent shares the name only; it is platform-neutral.
