# Agent org chart

Doctrine §5: design the org chart before the prompts. Every agent in the
1+Claude system is listed here, with its human anchor: the person whose
knowledge is its source of truth and whose sign-off gates its writes.
Snowflake keeps this file; a new agent is added before its first run.

| Agent | Function | Layer / scope | Model | Human anchor | Contracts it touches | Escalates to |
|---|---|---|---|---|---|---|
| snowflake | Architecture advisor (how would Snowflake Inc. proceed); contract registry and review desk | Whole system | opus | Blake | All (reviews) | Contract owner |
| salesforce | Vendor-perspective advisor: how would Salesforce Inc. proceed | CRM, integration, data platforms | opus | Blake | None (advises) | Panel, then Blake |
| chablis | Data acquisition with provenance | Data sourcing | sonnet | Blake | C2 | Snowflake |
| data-simplifier | Cleanup after changes; behavior and data preserved | Data layer: Python, SQL, schema | opus | Blake | C1 (producer side), C2 | Snowflake via review queue |
| experience-simplifier | Cleanup after changes; behavior preserved | Presentation layer: TS/React, HTML, CSS, templates | opus | Blake | C1 (consumer side) | Snowflake via review queue |

## Rules

- **One anchor per agent.** Today every anchor is Blake. As named people join
  a lane, the anchor moves to them; their corrections go into that agent's
  memory file and their sign-off gates its writes.
- **Writes stay single-threaded per contract.** Many agents may read a
  contract; one producer writes it.
- **Re-review on class change.** An agent whose output starts reaching people
  other than its anchor is re-reviewed (Doctrine amendment, 2026-11-18, §1).
