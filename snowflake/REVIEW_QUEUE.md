# Snowflake review queue

Where agents send anything they are not allowed to change themselves: a frozen
contract (`CONTRACTS.md`), a schema, a migration, a file format, or work that
belongs to another layer. The filing agent stops after filing.

**Snowflake** reviews each open item against `DOCTRINE.md` §8 and writes its
recommendation in the item. **The human owner** of the affected contract
decides. Nothing changes until the owner's decision is recorded.

This repo is public: describe the change, never private data. Point to the
private Drive folder "Chablis Data (private)" for anything sensitive.

Item format (C3):

```
### R<n> — <one-line title>
- Filed: YYYY-MM-DD by <agent>
- Contract / area: <C-id or file>
- Needed because: <the cleanup or feature that hit the limit>
- Proposed change: <what would change, and which consumers it touches>
- Snowflake review: <finding, evidence, risk, fix — §8>
- Decision: <owner, date, approve / reject / defer>
```

## Open

_None._

## Closed
