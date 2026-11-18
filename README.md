# chablis-feed (data branch)

Nightly output of the `chablis-feed` workflow, public lane: US-government
market and macro data (Treasury yield curve, FRED government series, CFTC
Commitments of Traders, SEC EDGAR filings and XBRL facts). Public domain.

- `feed/YYYY-MM-DD/manifest.json` — every source with its URLs, scope ("Silent on:"), license, row count, status
- `feed/YYYY-MM-DD/<SOURCE>.jsonl` — one record per line, each with source URL and retrieval time
- `logs/feed-YYYY-MM-DD.txt` — run log

Private-lane data (crypto, Yahoo, licensed vendors) never lands here.
