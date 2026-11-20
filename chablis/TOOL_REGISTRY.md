# Chablis tool registry

Every GitHub tool, library or Action vetted for a 1+Claude system. Scored with
the rubric in `DOCTRINE.md` §6 (Adoption, Upkeep, Security, Fit; 0–3 each).
Entries are `structural` class: review within ~90 days or they lapse to STALE.

No score is written without the evidence behind it. A blank score means not
yet scored, not zero.

## In use

| Tool | Where | Adoption | Upkeep | Security | Fit | Hard stop | Pin | Evidence | Scored | Review by |
|---|---|---|---|---|---|---|---|---|---|---|
| actions/checkout | morning-brief-data.yml (×2) | | | | | | **tag `@v4`, not SHA** — resolves today to `11d5960` (= v4.4.0) | `scout.py pins` 2026-11-18; `git ls-remote` tag `v4` = `v4.4.0`, 2026-11-19 | | |
| actions/checkout | chablis-scout.yml, chablis-feed.yml (×2 each) | | | | | | SHA `11d5960a…` (v4.4.0), lightweight tag so tag SHA = commit SHA | `git ls-remote`, 2026-11-18, re-verified 2026-11-19 | | |
| actions/checkout | chablis-keyed.yml (branch `chablis-keyed-setup`, not on main); chablis-probe.yml (commit `6051d73`, no live branch) | | | | | | **tag `@v4`, not SHA** | Actions API workflow list + file read at run SHAs, 2026-11-19; invisible to `scout.py pins` | | |
| actions/setup-python | morning-brief-data.yml | | | | | | **tag `@v5`, not SHA** — resolves today to `a26af69` (= v5.6.0) | `scout.py pins` 2026-11-18; `git ls-remote` tag `v5` = `v5.6.0`, 2026-11-19 | | |
| actions/setup-python | chablis-scout.yml, chablis-feed.yml | | | | | | SHA `a26af69b…` (v5.6.0), lightweight tag | `git ls-remote`, 2026-11-18, re-verified 2026-11-19 | | |
| actions/setup-python | chablis-keyed.yml, chablis-probe.yml (side branches, as above) | | | | | | **tag `@v5`, not SHA** | as above, 2026-11-19 | | |

Day 1 (2026-11-19) verified pins and where each Action is used; no dimension was
scored, because the 0–3 bands are not defined until Days 3–7. Newer majors exist
upstream (checkout v6.1.0, setup-python v6.3.0 per `git ls-remote`, 2026-11-19);
whether to move is a Fit question for Day 9. Security is unscored: the Scorecard API
could not be fetched in the 2026-11-19 run and the scout branch was empty.

## Candidates

Watchlist in `watchlist.json`; the nightly scout pulls their signals. Scored
by the learning path, week 1 onward.

Day 2 (2026-11-20) scored nothing. Adoption is scored from dependents, and none were
obtained: WebFetch was refused for `api.deps.dev` and `github.com/*/network/dependents`
(PROVENANCE_REQUIRED, unanswered permission request) and `scout.py` collects no dependents
(queue #14). Stars, forks and contributors are recorded in the Evidence column for the
five tools above and are not a substitute. Scout Scorecard coverage on 2026-11-19: 16 of
28 repos; 404 for 10, 406 for 2.

| Tool | Category | Adoption | Upkeep | Security | Fit | Hard stop | Evidence | Scored | Review by |
|---|---|---|---|---|---|---|---|---|---|
| scrapy/scrapy | crawling | | | | | | Day 2: stars 65,499, 381 default-branch commits in 90 d, Scorecard 7.1 (scout 2026-11-19; search re-read 2026-11-20: 65,508 stars). Dependents not pulled | | |
| apify/crawlee-python | crawling | | | | | | | | |
| dlt-hub/dlt | elt | | | | | | | | |
| meltano/meltano | elt | | | | | | | | |
| airbytehq/airbyte | elt | | | | | | | | |
| duckdb/duckdb | ledger-engine | | | | | | Day 2: stars 43,190, 11,889 default-branch commits in 90 d, MIT; Scorecard API 404 (scout 2026-11-19). Dependents not pulled | | |
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
| OpenBB-finance/OpenBB | market-data | | | | | | AGPL-3.0 per secondary sources, 2026-11-18 — internal use only under §10; confirm from the repo. Day 2: GitHub's licence detector returns NOASSERTION (scout 2026-11-19; search 2026-11-20), so AGPL stays unconfirmed. **Identity open:** `search/repositories` with `repo:OpenBB-finance/OpenBB` returns 422 on 2026-11-20; the 75.6k-star repo (created 2020-12-20, not a fork, homepage openbb.co) is listed under owner `openbq-org`. Move not confirmed from a second source (queue #16); hold any score until it is. Stars 75,567, 26 commits in 90 d (scout) | | |
| ccxt/ccxt | market-data | | | | | | | | |
| ranaroussi/yfinance | market-data | | | | | | Code Apache-2.0; Yahoo data personal use only (Yahoo API terms) — internal use only under §10. Day 2: stars 25,965, 87 default-branch commits in 90 d, Scorecard 5.6 (scout 2026-11-19; search re-read 2026-11-20: 25,968 stars). Dependents not pulled | | |
| dgunning/edgartools | market-data | | | | | | | | |
| mortada/fredapi | market-data | | | | | | Day 2: stars 1,675, 0 default-branch commits in 90 d, last push 2026-01-28, latest release v0.5.2 (2024-05-05); Scorecard API 404 (scout 2026-11-19). Dependents not pulled | | |
| databento/databento-python | market-data | | | | | | | | |
| alpacahq/alpaca-py | market-data | | | | | | | | |
| polygon-io/client-python | market-data | | | | | | Polygon.io renamed Massive 2025-10-30; client repo may have moved | | |

## Rejected

| Tool | Why | Date |
|---|---|---|
