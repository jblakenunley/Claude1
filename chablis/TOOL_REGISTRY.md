# Chablis tool registry

Every GitHub tool, library or Action vetted for a 1+Claude system. Scored with
the rubric in `DOCTRINE.md` §6 (Adoption, Upkeep, Security, Fit; 0–3 each).
Entries are `structural` class: review within ~90 days or they lapse to STALE.

No score is written without the evidence behind it. A blank score means not
yet scored, not zero.

## In use

| Tool | Where | Adoption | Upkeep | Security | Fit | Hard stop | Pin | Evidence | Scored | Review by |
|---|---|---|---|---|---|---|---|---|---|---|
| actions/checkout | morning-brief-data.yml | | | | | | **tag `@v4`, not SHA** | `scout.py pins`, 2026-11-18 | | |
| actions/checkout | chablis-scout.yml | | | | | | SHA `11d5960` (v4.4.0) | git ls-remote, 2026-11-18 | | |
| actions/setup-python | morning-brief-data.yml | | | | | | **tag `@v5`, not SHA** | `scout.py pins`, 2026-11-18 | | |
| actions/setup-python | chablis-scout.yml | | | | | | SHA `a26af69` (v5.6.0) | git ls-remote, 2026-11-18 | | |

## Candidates

Watchlist in `watchlist.json`; the nightly scout pulls their signals. Scored
by the learning path, week 1 onward.

| Tool | Category | Adoption | Upkeep | Security | Fit | Hard stop | Evidence | Scored | Review by |
|---|---|---|---|---|---|---|---|---|---|
| scrapy/scrapy | crawling | | | | | | | | |
| apify/crawlee-python | crawling | | | | | | | | |
| dlt-hub/dlt | elt | | | | | | | | |
| meltano/meltano | elt | | | | | | | | |
| airbytehq/airbyte | elt | | | | | | | | |
| duckdb/duckdb | ledger-engine | | | | | | | | |
| simonw/sqlite-utils | ledger-engine | | | | | | | | |
| great-expectations/great_expectations | validation | | | | | | | | |
| frictionlessdata/frictionless-py | validation | | | | | | | | |
| moj-analytical-services/splink | entity-resolution | | | | | | | | |
| dedupeio/dedupe | entity-resolution | | | | | | | | |
| J535D165/recordlinkage | entity-resolution | | | | | | | | |
| projectdiscovery/subfinder | recon-passive | | | | | | | | |
| owasp-amass/amass | recon-passive | | | | | | | | |
| gitleaks/gitleaks | secret-scanning | | | | | | | | |
| trufflesecurity/trufflehog | secret-scanning | | | | | | | | |
| ossf/scorecard | supply-chain | | | | | | | | |
| anthropics/claude-code-action | model-powered | | | | | | | | |
| OpenBB-finance/OpenBB | market-data | | | | | | AGPL-3.0 per secondary sources, 2026-11-18 — internal use only under §10; confirm from the repo | | |
| ccxt/ccxt | market-data | | | | | | | | |
| ranaroussi/yfinance | market-data | | | | | | Code Apache-2.0; Yahoo data personal use only (Yahoo API terms) — internal use only under §10 | | |
| dgunning/edgartools | market-data | | | | | | | | |
| mortada/fredapi | market-data | | | | | | | | |
| databento/databento-python | market-data | | | | | | | | |
| alpacahq/alpaca-py | market-data | | | | | | | | |
| polygon-io/client-python | market-data | | | | | | Polygon.io renamed Massive 2025-10-30; client repo may have moved | | |

## Rejected

| Tool | Why | Date |
|---|---|---|
