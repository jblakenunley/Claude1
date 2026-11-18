# Claude1
Clean exported code straight from Claude Prime

## Agents

| Agent | Role | Definition |
|---|---|---|
| Snowflake | Architecture advisor for AI agent and data-agent systems; runs a daily learning path | [`.claude/agents/snowflake.md`](.claude/agents/snowflake.md), [`snowflake/`](snowflake/) |
| Chablis | Data acquisition — ethical, novel sourcing with provenance; house expert on GitHub tool quality and selection; authorized recon. Runs a nightly scout and a daily learning path | [`.claude/agents/chablis.md`](.claude/agents/chablis.md), [`chablis/`](chablis/) |

## Claude Code handoff

Steps that need the Mac, a signed-in browser, GitHub settings or secrets are
queued in [`.claude/handoff/QUEUE.md`](.claude/handoff/QUEUE.md). In Claude Code
on the Mac, run `/handoff` to work the queue.
