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

## 2026-11-19 — Cycle 1, Day 2: The six-stage loop
**System:** morning-brief (`fetch.py`, `render.py`, `TASK.md`, `morning-brief-data.yml`)
**Finding:** Sensing is strong and fixed: sources are pinned in `config.json`; `fetch.py` runs a parser selftest, wraps each source in `safely()`, logs failures to `logs/DATE.txt`, and `validate` range-checks values. Reasoning is the model in TASK.md step 3: headline and verdict from the data file plus NWS wording, news chosen from feed candidates. Planning does not exist as a stage — the plan is the fixed task prompt, so the model never produces one. Coordination exists only system-to-system (the `mb-trigger-*` branch push and polling `mb-data`); no human sees the edition before it reaches his phone, and `check_edition`/`validate` are machine gates, not checkpoints. Acting is render → SendUserFile → PushNotification → archive. Learning is half-built: `record_calls`/`score_calls` score NWS snow calls against the median 24h depth gain at seven SNOTEL stations (NRCS confirms daily values are midnight readings, so the start-of-day assumption holds), but the scores go only to the archive — no step reads them back to qualify the next forecast line. The one working feedback is repeat-avoidance from the last three edition records.
**Risk:** A scorebook nobody consumes costs compute and gives the appearance of learning; a persistent NWS bias would keep reaching print unflagged.
**Fix:** Feed the 14-day hit rate and mean error into the `nws` block that `fetch.py nws` prints for the writer, so the forecast sentence is hedged when recent calls ran high or low. (Design detail is Day 4.)
**Doctrine change:** §2 — assessment is not learning: stage 6 counts only when a later run reads the outcome. Planning may be fixed in the prompt for a single-format pipeline; record that it is.
**Sources:** [NRCS Montana snow survey FAQ — SNOTEL first/end-of-day values are midnight readings, PST](https://www.nrcs.usda.gov/state-offices/montana/montana-snow-survey/frequently-asked-snow-survey-questions-montana)
