# Colleague agents: design

Design session of 2026-11-21. Objective (Blake): a low-cost team of agents that
supports a wide range of executive and creator use cases. Nothing off the table.
Optimise for minimum token spend and maximum use of the connectors and licences
already paid for.

## Recommendation

1. **Two kinds of colleague.** An *agent* runs in its own context and costs
   roughly 15x a chat turn (Anthropic's multi-agent figure). A *skill* is a
   playbook the main session loads for the cost of reading one file. So: agents
   only where independent judgment or a clean context earns the cost; every
   other lane is a skill.
2. **Six agents, seven skills.** The five existing agents stay. One agent is
   added: `reviewer`. Seven skills cover the use cases in the record.
3. **No chief-of-staff agent.** The main session is the coordinator, routed by
   the table in `CLAUDE.md`. That costs nothing extra; a coordinator agent would
   put a 15x layer on every request. Blake's decision (open question 2).
4. **Model tiers by Blake's rule** (pay where an undetected error costs more
   than the tokens):
   - **Opus**: `snowflake`, `salesforce`, `reviewer`. Judgment and
     verification.
   - **Sonnet**: `chablis`, `data-simplifier`, `experience-simplifier`.
     Mechanical or procedural work, checked by tests and the reviewer. The two
     simplifiers move from Opus to Sonnet; this is a separate commit, so it can
     be dropped without touching the rest.
   - **Haiku**: scheduled, settled jobs (reminders, formatting, merges) where
     the output is checked by a test or a human.
   Skills run on whatever model the session uses. Pick the session model by
   the same rule.
5. **Both code capabilities, one default.** Python for data; Claude's artifact
   types (Docs, Sheets, Slides, Dashboards) or Python-generated HTML for
   presentation. TypeScript/React comes into play when a product ships into
   someone else's surface: Salesforce Lightning Web Components for ERM on
   AgentExchange, or a client-installed interface. Both capabilities remain;
   the second is paid for when a project needs it.
6. **Judge code by outcomes.** Every PR states, in plain English: what
   behaviour changed, the acceptance checks Blake approved, whether the tests
   pass, and whether anything touched the review queue. Blake signs off on that
   summary, not on the diff.

## Use cases in the record, and the lane for each

| Lane (skill) | Use cases, from the artifact record | Output surface | Connectors |
|---|---|---|---|
| `exec-memo` | Digital stack executive summary, technology recommendations, event-first stack decision memo, ERM executive package, two-layer simplification practice | Docs | Docs, Drive |
| `record-verification` | Vetting dossier, register audit ledger, professional records, genealogy | Docs, Sheets | Web, Docs, Sheets, Drive (private) |
| `ecosystem-intel` | Dragonwing Signal, "Short the loop", Chablis source registry, ERM for Snapdragon, IoT framework, NFRM market brief | Dashboard, Docs | Web, Chablis feed, Drive |
| `creator-studio` | Book pitch, thesis, speaker bio, executive education series (guide, workbook, rubric), novel and teleseries | Docs, Slides | Docs, Drive |
| `career-desk` | Master resume, role applications, outreach | Docs, Gmail drafts | Docs, Gmail (drafts only), Drive |
| `client-advisory` | AI consulting pipeline, client engagements, agent handoff packages, market and business-model docs | Docs, Sheets, Slides | Docs, Sheets, Drive, Gmail drafts |
| `daily-ops` | Morning Brief, Snowcast, reminders | Scheduled task, Docs | Scheduled tasks, phone calendar and reminders, Gmail |

Agents these lanes call: `chablis` for data, the `snowflake` + `salesforce`
panel for platform decisions, `reviewer` before anything leaves Blake's hands.

## Connectors and licences

Use what is already paid for, in this order: the Claude plan's artifact types,
connectors and scheduled tasks; Google Workspace (Drive, Gmail); GitHub
Actions on the public repo; Claude Code on the Mac (through the handoff queue)
for anything that needs his machine. A new paid tool enters only after Chablis
scores it (`chablis/DOCTRINE.md` §6) and, if it is a platform, after the panel.
Gmail is draft-only: sending is Blake's.

## Cost controls

- Spawn an agent for a judgment call, never for typing.
- `reviewer` runs once per deliverable that leaves Blake's hands, not per draft.
- Simplifiers run once per PR, not after every edit.
- Scheduled tasks run on the lowest tier that passes their check.
- Skills stay short; reference material loads only when the step needs it.
- Tokens per session is a KPI (set 2026-08-22). Report it at the close of
  any multi-agent run.

## Human anchors

Every anchor is Blake today. Candidate anchors are named only in the private
Drive folder, never in this public repo, and an anchor moves to a person only
after that person agrees (open question 1).

## Open decisions (Blake's)

1. Anchors and consent for each lane.
2. Coordinator: main session (recommended) or a chief-of-staff agent.
3. Further panel lenses. Candidates: Microsoft (identity, Microsoft 365,
   Azure), plus a practitioner lens (Boris Cherny's task-anchored setup) for
   tooling decisions.
4. Write permissions: as drafted in `snowflake/ORG.md`. Skills write only to
   their output surface; structural changes go to the review queue.
5. Naming: company names for vendor lenses, personal names once a lane has a
   human anchor, function names until then.
