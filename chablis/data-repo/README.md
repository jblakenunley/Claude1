# claude1-data (private)

Private companion to the public `jblakenunley/claude1`. Everything Chablis
collects lives here; the public repo holds only code, doctrine and the registry.

| Path | Contents |
|---|---|
| `ledger/ledger.db` | Shared SQLite ledger for the whole portfolio (schema: `claude1/chablis/ledger/schema.sql`) |
| `scout/YYYY-MM-DD.json` | Nightly tool-quality signals from the scout workflow |
| `recon/` | Recon findings — authorization record first, then findings with method and time |
| `pulls/` | Raw landing files for large pulls, referenced from the ledger |
| `logs/` | Scout run logs |

Keep this repo private. Recon findings describe Blake's own exposure.
