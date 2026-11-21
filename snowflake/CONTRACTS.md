# Contract registry

Every interface where one part of the 1+Claude system hands work to another.
A listed contract is **frozen** for every agent. Agents simplify around it and
never change it. A change starts as an entry in `REVIEW_QUEUE.md`; Snowflake
reviews it against `DOCTRINE.md` §8; the contract's human owner decides.

The spec is the file named in **Defined by**. This registry does not restate
fields, so it cannot drift from the code.

| ID | Contract | Producer → consumer | Defined by | Human owner | Version |
|---|---|---|---|---|---|
| C1 | Morning brief data and edition files | `fetch.py` (data) and the daily writer (edition) → `render.py` + `template/` | `morning-brief/samples/data/*.json` and `samples/edition/*.json` (the shapes `render.py` reads) | Blake | 1 |
| C2 | Chablis ledger schema | `chablis/feed/feed.py` → `ledger.db` (private Drive) and every reader of it | `chablis/ledger/schema.sql` | Blake | 1 |
| C3 | Agent escalation format | any agent → Snowflake | `snowflake/REVIEW_QUEUE.md` (header) | Blake | 1 |

## Rules

1. **Registering.** A new agent or pipeline that hands data or output to
   another registers its contract here before its first run. Snowflake adds
   the row; the owner confirms it.
2. **Changing.** Bump the version, name the consumers that must change with
   it, and record the decision in the review queue entry. No silent edits.
3. **Owner.** Every row names a human. An agent can advise on a contract; it
   never owns one.
