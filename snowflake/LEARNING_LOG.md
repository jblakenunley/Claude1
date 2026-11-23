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

## 2026-11-20 — Cycle 1, Day 3: Coordination checkpoints
**System:** Chablis (agent file, `DOCTRINE.md` §7–8, ledger schema, handoff queue)
**Finding:** Chablis's only designed stage 4 is the §7 run contract, "state back before any run of size." "Of size" is undefined; the contract is said in the session, not written anywhere (the `pull` table has no contract field); nothing waits for a reply. In interactive runs that is visibility, not a checkpoint. Unattended runs have no human stage 4; the feed's plan is fixed in `feed_config.json` (acceptable per Day 2). The §8 recon authorization is self-recorded and checked by no one. The one checkpoint that does fire unattended is the harness permission prompt, and it fails closed: Day 1's 2 and Day 2's 15 WebFetch calls were refused with no one there to answer (queue #17). Queue `choice` items are a working batched checkpoint, used only for Mac-side work.
**Risk:** A new source, a credentialed pull, a use change (Day 1) or an active recon step can run on a contract no human saw. Any human sight of it is by chance.
**Fix (cheapest checkpoint):** Gate on novelty, not size. Known PUBLIC sources run without stopping. A new source, any CREDENTIALED/LICENSED pull, a personal→redistributable change, or any active recon step: Chablis writes the five-line contract as a `choice` row in `QUEUE.md` (private detail to Drive) and does not pull until the row is closed. No added tokens; Blake answers in the existing `/handoff` batch. Add a `contract` column to `pull` so the plan is kept with the run.
**Doctrine change:** §2 — a checkpoint is a plan a human sees *before* acting with the power to stop it; stating a plan without a pause is visibility. Gate checkpoints on novelty and class, not size.
**Sources:** none external.

## 2026-11-21 — Cycle 1, Day 4: Learning stage
**System:** morning-brief (`fetch.py` `score_calls`, `nws` subcommand; scores on `mb-data`, 2026-11-06 to 11-20)
**Finding:** No system closes the loop on outcomes; morning-brief's only read-back is repeat-avoidance (Day 2). The scorebook has 10 scored NWS calls (target days 11-13 to 11-19): 6 in band, 3 above, 1 below. Midpoint `error_in` averages +0.49 in, but 2.0 in of that 4.9 total comes from *hits*: a "0 to 1 inch" band on a dry day scores +0.5 though NWS was right. Error measured from the band edge is +0.25 in. Lead 0–1 day calls hit 5 of 7; lead 2 calls hit 1 of 3. Two of the three "high" misses are 1-inch calls against a 0 median depth gain, which settling can produce: depth can stay unchanged while new snow falls (avalanche.org). `score_calls` checks depth only, though `swe_in` is in the same records.
**Risk:** Feeding today's numbers to the writer would hedge NWS as running high on a sample where part of the bias is scoring artifact and part may be the gauge.
**Fix (the signal):** `fetch.py nws` prints one TRACK line for the writer: last 14 days' scored calls as in/above/below band, split by lead (0–1 d, 2 d). Score misses from the band edge, not the midpoint. A "high" counts only if median SWE gain is also under 0.1 in. STYLE rule: with ≥10 scored calls and misses ≥3:1 one way, the forecast sentence keeps NWS's band and drops firming words; no score figures print. On today's data it would not fire once the SWE check is applied, unless SWE confirms both 1-inch misses.
**Doctrine change:** §2 — a feedback signal must score the forecast on its own terms, against an observation the gauge can't hide, with a minimum sample before it changes output.
**Sources:** [avalanche.org — snow depth sensor: settling can leave depth unchanged despite new snow](https://avalanche.org/avalanche-encyclopedia/weather/weather-stations/snow-depth-sensor/)

## 2026-11-22 — Cycle 1, Day 5: Data agent: retrieval routing
**System:** morning-brief (`config.json`, `fetch.py run`, `TASK.md` steps 1–3)
**Finding:** Structured, script-retrieved: NRCS SNOTEL CSV (20 stations, two requests, ids pinned with a name guard); NWS point forecasts (22 points, two requests each); NWS alerts (3 points); CAIC zones (one GeoJSON, point-in-polygon); COtrip incidents and planned work (keyed, milepost-matched); Yahoo chart JSON for 12 markets, FRED fallback for the 10-yr only. Unstructured, script-retrieved: 31 RSS/Atom feeds (window-filtered, deduped, 12 per feed cap) and the NWS forecast discussion (sectioned, 900 chars). Unstructured, model-retrieved: playbook registries, resort pages, event links, and the fallback outlet search. Routing is static: every script source is pinned in `config.json`; the only run-time routes are Yahoo→FRED, the forecast-office lookup, Aspen Mountain reusing the summit forecast, the Monday 72h window, and the stale-cache refetch. Judgment applies only downstream (the writer picks stories from candidates). One mixed case carries weight: the snow bands the scorebook grades are regex-parsed from NWS prose (`snow_band`), while the points response the script already holds links `forecastGridData`, where NWS publishes `snowfallAmount` as a quantity.
**Risk:** A wording change NWS makes ("a dusting", "up to 2 inches") returns None, and the call goes unrecorded with no error, so the Day 4 signal thins without anyone seeing it.
**Fix:** Read `snowfallAmount` from `forecastGridData` as the primary snow call (one extra request at the summit point only); keep `snow_band` as the label and the fallback; log when the two disagree by more than one band. The grid field is reported missing at times, so the fallback stays.
**Doctrine change:** §3 — when a source publishes the same value structured and as prose, retrieve the structured form and keep the prose for wording; a parser over prose must log what it fails to parse.
**Sources:** [NWS API — gridpoints (raw forecast grid data)](https://weather-gov.github.io/api/gridpoints); [weather-gov/api #701 — snowfall amounts missing from /gridpoints](https://www.github.com/weather-gov/api/discussions/701)

## 2026-11-23 — Cycle 1, Day 6: Retrieval-time governance
**System:** ERM — not in this repo; worked from its one-line briefs (Salesforce package with LWC, Heroku-hosted service, multi-tenant endpoint records). No ERM design doc found in the repo or the private Drive.
**Finding:** No written policy says who may see which endpoint records, so enforcement cannot be checked against one. ERM has three retrieval paths, and each one enforces differently. (1) LWC/Apex in the customer org: sharing, FLS and object permissions apply only in user mode. User mode is the default from API 67.0; at 66.0 and earlier the default is system mode, so the package's API version decides this. (2) Agent actions: the agent queries as its assigned running user, not as the person who asked, and Apex or Flow actions in system mode bypass sharing (vendor-blog claim, consistent with the Apex doc). (3) The Heroku service: if it copies records through Heroku Connect, Heroku recommends View All for the integration user and does not support sharing rules as a filter. The Postgres copy then holds every record without the org's sharing, and tenant and user scoping exist only in ERM's own code.
**Risk:** On paths 2 and 3, a user or agent can read endpoint records their own Salesforce access would hide, across tenants on path 3. That is a company-class breach (Day 1).
**Fix:** Write a one-page access policy (role → record scope → path). Pin the package to API ≥67.0 or declare `WITH USER_MODE` explicitly. Give agent actions a least-privilege running user and no system-mode actions. On Heroku, key every query on tenant id and re-check the caller's record access before returning anything. Salesforce path Day 1 covers the integration user.
**Doctrine change:** §4 — governance holds at every copy and identity. A replica does not inherit its source's sharing model, and an agent's identity is not the asker's.
**Sources:** [Apex access mode](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexref/apex_classes_enforce_usermode.htm); [Heroku: sharing rules with Connect](https://help.heroku.com/7QQNUDRI/can-i-use-sharing-rules-to-restrict-record-visibility); [Obsidian: securing Agentforce](https://www.obsidiansecurity.com/academy/securing-salesforce-agentforce)
