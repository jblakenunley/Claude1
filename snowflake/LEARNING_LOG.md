# Snowflake — learning log

Newest entry last. Template:

```
## YYYY-MM-DD — Cycle C, Day N: <topic>
**System:** <system worked>
**Finding:** <what the exercise showed — evidence, not opinion>
**Risk:** <what it costs if left>
**Fix:** <smallest change that addresses it>
**Doctrine change:** none | <section and change>
**Sources:** <any external facts used, with links>
```

---

## 2026-11-18 — Cycle 1, Day 1: Personal vs company agents
**System:** all five, from their briefs (only morning-brief is in this repo)
**Finding:** Morning-brief is personal: one reader, his sources, no shared data. opc is company-class by design — built to be installed and operated by a client. ERM is company-class (multi-tenant endpoint records on Salesforce). Dragonwing Signal's inputs are public but its output goes to paying subscribers, so its delivery is company-class even though its retrieval is personal. Chablis is the drift case: built as his personal data-acquisition agent, but its readouts already feed investment theses and could feed Dragonwing or client work — at that point it serves others on data it sourced under personal-agent rules.
**Risk:** Chablis's source licensing, robots/denials handling and audit trail were set for a personal agent. Reusing its output for subscribers or clients without re-review imports personal-grade governance into company-grade delivery.
**Fix:** Tag each Chablis source with permitted use (personal / redistributable) at acquisition time; block anything untagged from leaving the personal class.
**Doctrine change:** §1 — "change of class" made explicit: an agent whose *output* reaches others is company-class for delivery even when retrieval stays personal.
**Sources:** none external.
