# Snowflake doctrine — architecture best practices for AI agents

Source: *A Practical Guide to AI Agents: Key agentic AI concepts, use cases and
considerations to drive ROI*, Snowflake Inc., December 2025 (21 pp.). Distilled
and paraphrased here as working doctrine; not a reproduction. Amended by the
daily learning path — every amendment is dated and traced to a log entry.

---

## 1. What kind of agent is it?

- **Personal agent** — acts for one person, sees that person's data, learns
  their habits. (Morning brief is one.)
- **Company agent** — works on shared organizational data, serves many users,
  bound by corporate policy. (Anything shipped to a client is one.)

The class decides the governance model. A personal agent that later serves a
team has changed class and must be re-reviewed.

## 2. The agent loop

Every agent design should be traceable to six stages:

| Stage | Question the design must answer |
|---|---|
| 1. Sensing | What is the task, and which sources are the most relevant, reliable, accurate and current? |
| 2. Reasoning | Where does the model interpret context, and what does it decide? |
| 3. Planning | How is a plan of action produced from that reasoning? |
| 4. Coordination | Where is the plan shared with users or other systems before execution? |
| 5. Acting | What executes, with what permissions? |
| 6. Learning | How are outcomes assessed and fed back into the next run? |

A design with no stage 4 has no checkpoint. A design with no stage 6 does not
improve; it only repeats.

## 3. The data agent

Enterprise value comes from internal data, so most serious agents are **data
agents**: they combine data and tools to produce data-grounded answers where
accuracy is the whole point. Three actions:

1. **Retrieval** — plan and route each request to the right structured
   (tables, sheets) or unstructured (PDFs, images, video, transcripts) source,
   **enforcing access and governance policy at retrieval time**.
2. **Tool and agent calls** — combine retrieval output with tools (charting,
   reporting) or hand to other agents that hold other tools.
3. **Output delivery** — chat reply, a table feeding a dashboard, a scheduled
   PDF to named recipients. Delivery is part of the design, not an afterthought.

Specialize. A data agent is scoped to a business function; sales and R&D get
different agents over different data.

## 4. Three requirements for retrieval

1. **Accuracy.** Wrong data makes the whole workflow worthless, however good
   the charts.
2. **Efficiency.** Too much accessible data inflates compute cost; too little
   hurts accuracy. Source selection is a cost control.
3. **Governance.** A single scalable framework for access and privacy controls,
   able to cover hundreds or thousands of agents. Agents get access the way
   employees do — scoped, revocable, audited.

Primary architectural components: a retrieval tool for structured data
(text-to-SQL is the hard part — models do not natively understand rows and
columns), a retrieval tool for unstructured data (preparation maturity is the
usual gap), both sitting on prepared, governed data.

## 5. Multi-agent structure

Agents need "managers" and "cross-functional teams" the way an org does: an
orchestrating layer that routes work to specialists, each with its own data and
tools. Design the org chart before the prompts.

## 6. Trust layer

| | Guardrails | Evaluation | Observability |
|---|---|---|---|
| What | Business policy given to the model to filter harmful content, block denied topics, strip specified terms | Quantitative test scores on accuracy, consistency, safety, reliability — benchmarks plus real-world tests | Continuous evaluation of live responses: performance, behavior, interaction with data sources |
| Why | Responses stay inside policy and values | Responses are relevant, safe, high quality | Detects drift and model changes that move answers |

Plus three practices:

- **Human handoff.** The agent must detect its own uncertainty, recognize
  queries beyond its competence, and escalate. Define when and to whom up
  front — especially in high-stakes domains. Build the feedback loop in from
  the start; collecting and acting on feedback is where most teams stall.
- **Explainability.** The agent states its rationale: key data points and the
  reasoning path. Back it with audit logs, interpretability tooling, and
  manual reviews where the model is made to show its steps. Expect a trade-off
  against performance.
- **Ethics and bias.** Red-team, audit training and source data for diversity,
  and define an escalation path for when an action breaches policy.

## 7. Accuracy tolerance is a design input

The claims-agent case (Accenture on Snowflake) is the most useful idea in the
source: insurance claims tolerate imperfect accuracy — customers accept partial
payouts for speed, decisions are internally appealable, regulation is lighter.
Fiduciary advice tolerates none. **Set the accuracy bar per domain before
choosing architecture**, and keep a human in the loop in proportion to the
cost of a wrong answer.

## 8. Review protocol — five principles plus rollout

Use this to assess any design. For each item: finding, evidence, risk, fix.

**Architecture principles**
1. **Scalability** — does it hold as models, agents and users multiply?
2. **Flexibility** — does it integrate with the rest of the stack (data
   sources, models, collaboration tools) and survive a model swap?
3. **Data accessibility** — first-, second- and third-party data, structured
   and unstructured, reachable and current (real or near-real time where it
   matters)?
4. **Trust** — guardrails, evals, observability present, and the
   agent-to-human handoff defined?
5. **Security and compliance** — granular access controls on data and
   models, proactive log monitoring?

**Rollout readiness**
1. Technology foundation assessed (processing, natural-language retrieval,
   deployment)?
2. Tied to a named business goal and use case?
3. Purpose communicated by leadership?
4. Change management — users trained to work with it and to give feedback?
5. Governance, compliance and human oversight in place, with a way to track
   changing regulation?

## 9. What the source does not cover

The guide is an introductory vendor ebook. It is silent or thin on the
following; Snowflake answers these from the learning log and current sources,
never from the guide:

- Token and compute cost accounting; model-tier routing
- Prompt injection and tool-trust boundaries (data that carries instructions)
- Evaluation method — how to build a test set, what to measure, pass bars
- Evidence freshness — when retrieved data stops being current (see the
  per-class time-to-live model in the 1+Claude freshness workstream)
- Failure classes specific to LLM output (see register doctrine)
- Concrete orchestration patterns and their failure modes

## 10. Vendor claims — do not use as load-bearing

The source cites: 82% of large enterprises planning agents within three years;
10% currently using them; 37% of 2024 VC to AI startups; agentic AI making 15%
of daily work decisions by 2028; 14% more issues resolved per hour; 90% less
prospecting time; a $47.1B market by 2030. These are survey and forecast
figures in vendor marketing. Cite them only as "Snowflake reports," and never
as the basis for a recommendation without an independent source.

---

## Amendments

Each amendment: date, section, change, log entry that drove it.

- **2026-11-18, §1.** Class is set by output as well as input: an agent whose output reaches people other than its owner is company-class for delivery, even if its retrieval stays personal. (Log: Cycle 1, Day 1.)
- **2026-11-19, §2.** Assessment is not learning: stage 6 is present only when a later run reads the scored outcome and changes behavior. A scorebook written only to an archive is stage-6 instrumentation, not stage 6. A planning stage may legitimately be fixed in the prompt for a single-format pipeline, but the review must record that it is fixed. (Log: Cycle 1, Day 2.)
- **2026-11-20, §2.** Stage 4 needs a pause: a checkpoint is a plan a human (or a named system) sees before execution with the power to stop it. A plan stated with no wait is visibility, not coordination. Trigger checkpoints on novelty and class (new source, credentialed or licensed access, change of use, active steps), not on an undefined "size", and route unattended ones to an existing batched channel rather than a prompt that fails closed. (Log: Cycle 1, Day 3.)
- **2026-11-21, §2.** A stage-6 feedback signal must (a) score the output on its own terms (in/out of a stated band, not distance from a midpoint the forecaster never claimed), (b) be checked against an observation the measurement cannot mask (e.g. SWE alongside depth), and (c) carry a minimum sample and a direction threshold before it changes what the next run says. (Log: Cycle 1, Day 4.)
- **2026-11-22, §3.** Route to the structured form: when a source publishes the same value both as a quantity and as prose, retrieval takes the quantity and keeps the prose only for wording. Any parser over prose must log what it fails to parse, so a silent None never thins a downstream signal. (Log: Cycle 1, Day 5.)
- **2026-11-23, §4.** Retrieval-time governance holds at every copy and every identity. A replica (sync, cache, warehouse) does not inherit its source's sharing model, so the copy re-enforces tenant and record scope itself. An agent retrieves as its own running user, not as the asker, so its actions run least-privilege and in user mode, and any system-mode path is listed and justified. Write the access policy first (role → record scope → retrieval path); enforcement cannot be audited without one. (Log: Cycle 1, Day 6.)
- **2026-11-24, §2.** Acting includes delivery, and delivery must fail loudly. A delivery step distinguishes "nothing to deliver" from "delivery failed" and gives them different exits, so the platform's own failure alerting can fire; a swallowed error that ends green is no handling. Every delivery writes a record (channel, artifact, success) that a later run can read, so a missed edition is distinguishable from no edition. (Log: Cycle 1, Day 7.)
- **2026-11-25, §6.** Accuracy needs a second reference. Every retrieved value is checked against something independent of its source (another source, a calendar of when the value can exist, or a plausible range), and each value records which source served it. A fallback that fires only when a response fails to parse protects availability, not accuracy. (Log: Cycle 1, Day 8.)
