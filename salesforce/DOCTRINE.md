# Salesforce doctrine: how Salesforce Inc. would proceed

Distilled and paraphrased from Salesforce's own published architect guidance,
read 2026-11-21 (sources at the end). Working doctrine, not a reproduction.
Amended by the daily learning path; every amendment is dated and traced to a
log entry.

This is one vendor's playbook, argued faithfully. It is not a platform
decision. Read it alongside `snowflake/DOCTRINE.md`.

---

## 1. The frame: Well-Architected

Salesforce judges a solution by three capabilities, each with behaviors:

| Capability | Means | Behaviors |
|---|---|---|
| Trusted | Protects the business and its stakeholders | Secure, compliant, reliable |
| Easy | Delivers value fast | Intentional, automated, engaging |
| Adaptable | Evolves with the business | Resilient, composable |

Salesforce began revising the framework for agent-based systems at Dreamforce
2026. Check the live version before citing a behavior that may have moved.

## 2. How Salesforce chooses an integration approach

Its data-integration decision guide weighs six things:

1. What is already in place (ESB/ETL, compliance needs, cloud or on-premise)
2. The data flow: synchronous or asynchronous, which system is the source of
   truth, direction, exception handling, how tightly coupled
3. Implementation effort and who will deliver it
4. Maintainability, skills and total cost of ownership
5. Data volume, including large data volumes and bulk loads
6. Limits: transformation complexity, multiple sources, call frequency

**Its first rule: avoid replicating data unless it is needed.** Prefer
reading data where it lives (Salesforce Connect, API access) over copying it.
If an ESB, ETL tool or MuleSoft is already in place, use it.

## 3. The integration patterns

Salesforce's reference patterns, used by its own consulting architects:

| Pattern | What happens | Timing |
|---|---|---|
| Request and reply | Salesforce calls a remote process and waits for the answer | Synchronous |
| Fire and forget | Salesforce starts a remote process and moves on; the remote side owns errors | Asynchronous |
| Batch data synchronization | Records are refreshed in batches, in either direction | Asynchronous |
| Remote call-in | An outside system creates, reads, updates or deletes Salesforce data | Either |
| UI update on data change | The Salesforce screen refreshes when data changes | Asynchronous |
| Data virtualization | Salesforce reads outside data live without storing it | Synchronous |

Pick by **type** (process, data, or virtual) and **timing** (synchronous or
asynchronous).

## 4. When an outside data platform is involved: Data 360

Salesforce's Data 360 interoperability guide sets out the options for working
with Snowflake, Databricks, BigQuery, Redshift or object storage:

| Option | Use when | Main trade-off |
|---|---|---|
| Ingestion (copy into Data 360) | Customer profiles, compliance, central campaigns: control and audit matter | Real-time ingestion costs the most; batch is cheaper but stale |
| Zero Copy live query | Occasional queries where freshness is critical | Pay per query; cost spikes at high query rates |
| File federation (Iceberg on S3, ADLS, GCS) | Very large historical data, ML training | Cheapest storage; no freshness guarantee |
| Cached acceleration | Frequent queries on slowly changing data | Refresh cost; deleted records linger until a full refresh |
| Hybrid | Ingest the governed core, federate the volatile bulk | More moving parts |

Salesforce's rule of thumb: data read often but changed rarely → cache it;
data changed often relative to how often it is read → live query or ingest.

**What Salesforce does not say here:** Data 360 is itself a licensed product
consumed in credits. Every option in this section assumes you have it. A
project with no Data 360 falls back to §3.

## 5. Recommendations and cautions Salesforce publishes

- Use a dedicated "API Only" integration user, and Salesforce's current
  external client app model for sign-in and authorization.
- Use Data 360 to harmonize data from many sources.
- **Avoid:** Outbound Messaging (no further investment), Salesforce to
  Salesforce (end of life), the Replication API. Don't base an integration
  strategy on Data Loader or the CLI.
- Make callouts from triggers only asynchronously; avoid mixed-transaction
  writes.
- Plan for limits: API request allocations, Apex governor limits, MuleSoft
  capacity. Enabling Shield Platform Encryption changes some behaviors.

## 6. Practices that hold on any platform

- **Errors:** in request and reply the caller retries and Salesforce commits
  only on success; in fire and forget the remote side owns recovery. Platform
  events can be replayed for a limited window. Middleware for complex
  recovery.
- **Idempotency:** assume calls repeat. Use unique message IDs and upsert on
  an external ID.
- **Security:** HTTPS only, least-privilege integration users, signatures for
  request integrity, firewalls and allow-lists on the remote side.

## 7. Where Salesforce has a commercial interest

Name these in every answer (per the agent's rule 3):

- Data 360 licences and credits (every option in §4)
- MuleSoft, wherever middleware is recommended
- Agentforce, wherever agents act on CRM data
- Tableau, wherever analytics sits on top
- Heroku, wherever a custom service runs beside the org

## 8. Review protocol

For any design, report finding, evidence, risk and fix against:

1. **Trusted:** access controlled per user and integration user; compliance
   requirements mapped; failure and retry defined
2. **Easy:** the simplest pattern that meets the need (§2 rule: no needless
   replication)
3. **Adaptable:** survives a change of platform, org or volume
4. **Pattern fit:** type and timing match §3
5. **Limits:** API allocations and governor limits checked against expected
   volume
6. **The no-new-platform option:** could standard Salesforce integration do
   this without an outside data layer?

## 9. What this source does not cover

- Neutral cost comparison with non-Salesforce routes
- Token and model cost for agents acting on CRM data
- Prompt injection through CRM records (customer-entered text reaching an
  agent)
- Evaluation method for agent output
- Evidence freshness beyond each tool's refresh settings

Answer these from the learning log and current, cited sources.

---

## Sources (read 2026-11-21)

- [Salesforce Well-Architected overview](https://architect.salesforce.com/well-architected/overview)
- [Data Integration decision guide](https://architect.salesforce.com/decision-guides/data-integration)
- [Integration Patterns and Practices, v64.0, Summer '25](https://resources.docs.salesforce.com/256/latest/en-us/sfdc/pdf/integration_patterns_and_practices.pdf)
- [Data 360 Interoperability decision guide](https://architect.salesforce.com/docs/architect/decision-guides/guide/data-360-interoperability)
- [Introducing the new Well-Architected Framework](https://www.salesforce.com/blog/new-well-architected-framework/)

## Amendments

_None yet._
