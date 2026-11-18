# Snowflake — daily learning path

One lesson a day, 30 days a cycle. Each lesson = one topic, one exercise run
against a real system, one logged finding. Weeks 1–3 work the doctrine;
week 4 and the close cover what the source leaves out, where most of the
value is.

Systems referenced: **morning-brief** (in this repo: `fetch.py`, `render.py`,
`.github/workflows/morning-brief-data.yml`), **Chablis** (data acquisition),
**opc** (1+Claude scaffold), **ERM** (Endpoint Relationship Management on
Salesforce), **Dragonwing Signal** (Qualcomm ecosystem brief). For a system not
in this repo, work from its brief or published artifact and say so in the log.

Rules for every lesson: verify any external fact before logging it; log
findings, not verdicts; record the tokens the lesson cost if the runtime
reports them.

## Week 1 — The agent and its data (Doctrine §1–5)

| Day | Topic | Exercise |
|---|---|---|
| 1 | Personal vs company agents | Classify each of the five systems. Flag any that is drifting from personal to company. |
| 2 | The six-stage loop | Map morning-brief onto sensing → learning. Name the missing stages. |
| 3 | Coordination checkpoints | Where does a human see Chablis's plan before it acts? Propose the cheapest checkpoint. |
| 4 | Learning stage | Does any system feed outcomes back into its next run? Design one feedback signal for morning-brief. |
| 5 | Data agent: retrieval routing | Inventory morning-brief's sources: structured vs unstructured, how each is chosen. |
| 6 | Retrieval-time governance | For ERM: who may see which endpoint records, and where is that enforced? |
| 7 | Output delivery as design | List every delivery channel across the five systems; flag any with no failure handling. |

## Week 2 — Retrieval and trust (Doctrine §4, §6)

| Day | Topic | Exercise |
|---|---|---|
| 8 | Accuracy | Pick one morning-brief data point; trace it to source; state how a wrong value would surface. |
| 9 | Efficiency | Estimate what morning-brief retrieves vs what it uses. Name the waste. |
| 10 | Text-to-SQL | Study current text-to-SQL approaches (semantic layers, schema descriptions). Assess for ERM on Salesforce. |
| 11 | Unstructured prep | Chunking, extraction, metadata. Assess Dragonwing's source documents against it. |
| 12 | Guardrails | Write the guardrail policy Chablis needs (robots/denials, licensing, PII). |
| 13 | Evaluation | Draft a 10-item eval set for morning-brief with pass criteria. |
| 14 | Observability | What would tell you morning-brief silently degraded? Specify the minimum signal. |

## Week 3 — Humans, explainability, architecture (Doctrine §6–8)

| Day | Topic | Exercise |
|---|---|---|
| 15 | Human handoff | Define uncertainty triggers and escalation targets for Chablis. |
| 16 | Explainability | Specify the rationale block each Dragonwing claim should carry. |
| 17 | Accuracy tolerance | Rate each system's domain on the claims-vs-fiduciary scale; set its bar. |
| 18 | Scalability | Stress-test opc: what breaks at 10 agents, at 10 clients? |
| 19 | Flexibility | Model-swap test: what in each system assumes a specific model or vendor? |
| 20 | Security and compliance | Secrets, access scopes and logs in this repo's GitHub workflow. |
| 21 | Rollout readiness | Run the §8 rollout checklist against ERM as a client offering. |

## Week 4 — Beyond the source (Doctrine §9)

| Day | Topic | Exercise |
|---|---|---|
| 22 | Token and compute cost | Build a per-run cost line for morning-brief. Verify current model pricing; cite it. |
| 23 | Model-tier routing | Which steps in each system need a frontier model and which do not? |
| 24 | Prompt injection | Map every place untrusted content reaches a model in Chablis; name the boundary. |
| 25 | Evidence freshness | Apply per-class time-to-live horizons to morning-brief's sources. |
| 26 | LLM failure classes | Run the register-doctrine failure classes against one Snowflake log entry of your own. |
| 27 | Orchestration patterns | Study orchestrator/worker, routing, and evaluator loops; pick one for opc and say why. |
| 28 | Platform comparison | Compare two data-agent platforms on governance and cost. Verify both sides. |

## Close

| Day | Topic | Exercise |
|---|---|---|
| 29 | Doctrine revision | Fold the cycle's findings into `DOCTRINE.md`; date each amendment. |
| 30 | Full review | Run the amended §8 protocol end-to-end on Chablis. One page. |

Cycle 2 reruns every exercise against the amended doctrine and logs what
changed.
