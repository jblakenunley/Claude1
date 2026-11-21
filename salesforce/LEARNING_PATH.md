# Salesforce — daily learning path

One lesson a day, 30 days a cycle. Each lesson = one topic, one exercise run
against a real system, one logged finding. Weeks 1–3 work the doctrine;
week 4 covers what the source leaves out.

Systems referenced: **ERM** (Endpoint Relationship Management on Salesforce,
Heroku-hosted service), **Aspen Community Church** (Salesforce CRM),
**morning-brief** and **Chablis** (in this repo), **opc** (1+Claude scaffold).
For a system not in this repo, work from its brief or published artifact and
say so in the log.

Rules for every lesson: verify any external fact against Salesforce's live
documentation before logging it; log findings, not verdicts; include "when
Salesforce would not be the answer" in every finding; record the tokens the
lesson cost if the runtime reports them.

## Week 1 — Well-Architected (Doctrine §1, §8)

| Day | Topic | Exercise |
|---|---|---|
| 1 | Trusted: secure | Map ERM's sign-in and integration user against least privilege. |
| 2 | Trusted: compliant | List the compliance duties ERM's endpoint records carry; where each is enforced. |
| 3 | Trusted: reliable | Name ERM's failure modes at the Salesforce boundary and the retry for each. |
| 4 | Easy: intentional | Is ERM using the simplest pattern that meets the need? Name any extra moving part. |
| 5 | Easy: automated | Which ERM steps run by hand today and what would automate them in Salesforce's playbook? |
| 6 | Adaptable: resilient | What in ERM breaks if the customer's org changes edition or volume? |
| 7 | Adaptable: composable | Draw ERM's components and their boundaries; flag tight coupling. |

## Week 2 — Patterns and decision criteria (Doctrine §2, §3, §5)

| Day | Topic | Exercise |
|---|---|---|
| 8 | The six decision criteria | Run them against the church CRM's data flows. |
| 9 | Request and reply | Find one ERM flow that fits; state its error handling. |
| 10 | Fire and forget | Same, for an asynchronous ERM flow. |
| 11 | Batch synchronization | Would any ERM or church data move in batches? Name the source of truth. |
| 12 | Remote call-in | How does the Heroku service write to Salesforce; what limits apply? |
| 13 | Data virtualization | Could ERM show endpoint data in Salesforce without storing it there? |
| 14 | Cautions | Check ERM's design against §5's avoid-list. |

## Week 3 — Outside data platforms (Doctrine §4, §7)

| Day | Topic | Exercise |
|---|---|---|
| 15 | When Data 360 is warranted | For each system, would Salesforce propose Data 360? Name its gain (§7). |
| 16 | Ingestion vs live query | Apply the rule of thumb to Chablis's ledger if it ever fed a CRM. |
| 17 | Caching and stale deletes | Where would cached acceleration's lingering deletes cause harm? |
| 18 | Hybrid | Design the hybrid split for a hypothetical ERM-with-warehouse. |
| 19 | Other warehouses | Verify current Zero Copy support for Snowflake, Databricks, BigQuery, Redshift; cite. |
| 20 | Panel run | Run the panel protocol with snowflake on one real question; log where you disagreed. |
| 21 | Commercial interest | For three past recommendations, list what Salesforce would have gained. |

## Week 4 — Beyond the source (Doctrine §9)

| Day | Topic | Exercise |
|---|---|---|
| 22 | Agentforce cost | Verify current Agentforce pricing model; build a per-action cost line; cite. |
| 23 | Model-tier routing | Which CRM-facing agent steps need a frontier model? |
| 24 | Prompt injection via CRM | Trace where customer-entered text in a record could reach an agent. |
| 25 | Evidence freshness | Apply per-class time-to-live horizons to CRM fields an agent reads. |
| 26 | LLM failure classes | Run the register-doctrine failure classes against one of your own log entries. |
| 27 | Framework revision | Check what changed in the Dreamforce 2026 Well-Architected revision; amend §1. |
| 28 | No-platform option | For ERM, write the case for standard integration with no outside data layer. |

## Close

| Day | Topic | Exercise |
|---|---|---|
| 29 | Doctrine revision | Fold the cycle's findings into `DOCTRINE.md`; date each amendment. |
| 30 | Full review | Run the amended §8 protocol end-to-end on ERM. One page. |

Cycle 2 reruns every exercise against the amended doctrine and logs what
changed.
