# Chablis tool registry

Every GitHub tool, library or Action vetted for a 1+Claude system. Scored with
the rubric in `DOCTRINE.md` §6 (Adoption, Upkeep, Security, Fit; 0–3 each).
Entries are `structural` class: review within ~90 days or they lapse to STALE.

No score is written without the evidence behind it. A blank score means not
yet scored, not zero.

## In use

| Tool | Where | Adoption | Upkeep | Security | Fit | Hard stop | Pin | Evidence | Scored | Review by |
|---|---|---|---|---|---|---|---|---|---|---|
| actions/checkout | morning-brief-data.yml (×2) | | 1 | | | | **tag `@v4`, not SHA** — resolves today to `11d5960` (= v4.4.0) | `scout.py pins` 2026-11-18; `git ls-remote` tag `v4` = `v4.4.0`, 2026-11-19. **Upkeep 1 (Day 3, `chablis/upkeep.py`, git history as of 2026-11-21; tool score, same on every checkout row):** L1 last human commit 2026-07-20 (124 d); R2 latest v7.0.1 2026-07-17 (127 d), 6 release days in 365 d, among them tags for v2.8.0, v3.7.0, v4.4.0 and v6.1.0 on 2026-07-16 (commit message "backport fixes to releases-vN"); 0 commits in 90 d (scout 0; Scorecard Maintained 0); scout `pushed_at` 2026-10-17 is dependabot branches; 17 human commits of 31 in 365 d, 3 authors, bus not scored (n<20). Band-failure candidate for Day 7. | 2026-11-21 (Upkeep only) | 2027-02-19 |
| actions/checkout | chablis-scout.yml, chablis-feed.yml (×2 each) | | 1 | | | | SHA `11d5960a…` (v4.4.0), lightweight tag so tag SHA = commit SHA | `git ls-remote`, 2026-11-18, re-verified 2026-11-19. Upkeep: as the `morning-brief-data.yml` row (Day 3). | 2026-11-21 (Upkeep only) | 2027-02-19 |
| actions/checkout | chablis-keyed.yml (branch `chablis-keyed-setup`, not on main); chablis-probe.yml (commit `6051d73`, no live branch) | | 1 | | | | **tag `@v4`, not SHA** | Actions API workflow list + file read at run SHAs, 2026-11-19; invisible to `scout.py pins` Upkeep: as the `morning-brief-data.yml` row (Day 3). | 2026-11-21 (Upkeep only) | 2027-02-19 |
| actions/setup-python | morning-brief-data.yml | | 3 | | | | **tag `@v5`, not SHA** — resolves today to `a26af69` (= v5.6.0) | `scout.py pins` 2026-11-18; `git ls-remote` tag `v5` = `v5.6.0`, 2026-11-19. **Upkeep 3 (Day 3, `chablis/upkeep.py`, 2026-11-21; tool score, same on every setup-python row):** L3 last human commit 2026-11-19; R3 v7.1.0 2026-10-21, 5 release days in 365 d; 17 commits in 90 d but 14 are dependabot (3 human); 23 human commits in 365 d, 12 authors, absence factor 3, no deduction. | 2026-11-21 (Upkeep only) | 2027-02-19 |
| actions/setup-python | chablis-scout.yml, chablis-feed.yml | | 3 | | | | SHA `a26af69b…` (v5.6.0), lightweight tag | `git ls-remote`, 2026-11-18, re-verified 2026-11-19. Upkeep: as the `morning-brief-data.yml` row (Day 3). | 2026-11-21 (Upkeep only) | 2027-02-19 |
| actions/setup-python | chablis-keyed.yml, chablis-probe.yml (side branches, as above) | | 3 | | | | **tag `@v5`, not SHA** | as above, 2026-11-19. Upkeep: as the `morning-brief-data.yml` row (Day 3). | 2026-11-21 (Upkeep only) | 2027-02-19 |

Day 1 (2026-11-19) verified pins and where each Action is used; no dimension was
scored, because the 0–3 bands are not defined until Days 3–7. Newer majors exist
upstream (checkout v6.1.0, setup-python v6.3.0 per `git ls-remote`, 2026-11-19);
whether to move is a Fit question for Day 9. Security is unscored: the Scorecard API
could not be fetched in the 2026-11-19 run and the scout branch was empty.

Day 3 (2026-11-21) scored Upkeep only, with `chablis/upkeep.py` (bands in `DOCTRINE.md` §6); Adoption, Security and Fit stay blank. Correction to the Day 1 paragraph above: newer majors than v6.1.0 and v6.3.0 exist. `git ls-remote --tags`, 2026-11-21: checkout `v7` = `v7.0.1` = `3d3c42e5…` (2026-07-17), setup-python `v7` = `v7.1.0` = `6d4fd22b…` (2026-10-21), both lightweight tags, so tag SHA = commit SHA. The pins above still hold: checkout `v4` = `v4.4.0` = `11d5960a…` (a backport commit tagged 2026-07-16) and setup-python `v5` = `v5.6.0` = `a26af69b…`.

## Candidates

Watchlist in `watchlist.json`; the nightly scout pulls their signals. Scored
by the learning path, week 1 onward.

Day 3 (2026-11-21) scored Upkeep for scrapy, duckdb, yfinance, fredapi and OpenBB (rows below). Day 2 (2026-11-20) scored nothing. Adoption is scored from dependents, and none were
obtained: WebFetch was refused for `api.deps.dev` and `github.com/*/network/dependents`
(PROVENANCE_REQUIRED, unanswered permission request) and `scout.py` collects no dependents
(queue #14). Stars, forks and contributors are recorded in the Evidence column for the
five tools above and are not a substitute. Scout Scorecard coverage on 2026-11-19: 16 of
28 repos; 404 for 10, 406 for 2.

| Tool | Category | Adoption | Upkeep | Security | Fit | Hard stop | Evidence | Scored | Review by |
|---|---|---|---|---|---|---|---|---|---|
| scrapy/scrapy | crawling | | 2 | | | | Day 2: stars 65,499, 381 default-branch commits in 90 d, Scorecard 7.1 (scout 2026-11-19; search re-read 2026-11-20: 65,508 stars). Dependents not pulled. **Upkeep 2 (Day 3, `chablis/upkeep.py`, git history as of 2026-11-21):** L3 last human commit 2026-11-19; R3 latest 2.20.0 on 2026-11-06, 11 release days in 365 d; bus: top author made 52% of 825 human commits in 365 d (56% of 375 in 90 d), top two 85% / 91%, absence factor 1, so -1. 381 commits in 90 d = scout 381 = `search/commits` 381. | 2026-11-21 (Upkeep only) | 2027-02-19 |
| apify/crawlee-python | crawling | | | | | | | | |
| dlt-hub/dlt | elt | | | | | | | | |
| meltano/meltano | elt | | | | | | | | |
| airbytehq/airbyte | elt | | | | | | | | |
| duckdb/duckdb | ledger-engine | | 3 | | | | Day 2: stars 43,190, 11,889 default-branch commits in 90 d, MIT; Scorecard API 404 (scout 2026-11-19). Dependents not pulled. **Upkeep 3 (Day 3, `chablis/upkeep.py`, 2026-11-21):** L3 last human commit 2026-11-20; R3 v2.0.1 2026-11-19, 12 release days in 365 d (two lines maintained: v1.4.5 2026-06-14, v1.5.4 2026-06-16); bus: 449 human authors in 365 d, top author 14%, absence factor 9. 12,181 commits in 90 d vs scout 12,188 (2026-11-20). | 2026-11-21 (Upkeep only) | 2027-02-19 |
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
| OpenBB-finance/OpenBB | market-data | | 2 | | | | AGPL-3.0 per secondary sources, 2026-11-18, **now superseded**: `LICENSE` is Apache-2.0 on `main` (869cfed1) and `develop` (f0f1852b), last changed by "V5 (#7489)" 2026-09-29 (`git show`, 2026-11-21); GitHub's detector still returns NOASSERTION (scout 2026-11-19; search 2026-11-20). Fit not scored; Apache-2.0 would clear §10 either way. **Identity:** openbb.co/company/open (edit dated 2026-10-01) names OpenBQ, github.com/openbq-org, as steward organization; `git ls-remote` answers HTTP 200 with HEAD f0f1852b for both OpenBB-finance/OpenBB and openbq-org/OpenBB (2026-11-21); `search/repositories` for the old name was 422 on 2026-11-20. The org move is confirmed from OpenBB's own site and the history is identical under both names; which owner GitHub treats as canonical is not (queue #16). Stars 75,602, 26 commits in 90 d (scout 2026-11-20). **Upkeep 2 (Day 3, `chablis/upkeep.py`, 2026-11-21):** L3 last human commit 2026-11-18; R3 `openbb-v5.0.0` 2026-09-29 (per-package tags in one repo: 8 release days in 365 d); bus: top author 58% of 133 human commits in 365 d, absence factor 1, so -1 (factor 2 over 90 d). 26 commits in 90 d = scout. | 2026-11-21 (Upkeep only) | 2027-02-19 |
| ccxt/ccxt | market-data | | | | | | | | |
| ranaroussi/yfinance | market-data | | 2 | | | | Code Apache-2.0; Yahoo data personal use only (Yahoo API terms) — internal use only under §10. Day 2: stars 25,965, 87 default-branch commits in 90 d, Scorecard 5.6 (scout 2026-11-19; search re-read 2026-11-20: 25,968 stars). Dependents not pulled. **Upkeep 2 (Day 3, `chablis/upkeep.py`, 2026-11-21):** L3 last human commit 2026-11-07; R3 1.8.0 2026-11-03, 13 release days in 365 d; bus: top author 54% of 386 human commits in 365 d (55% of 87 in 90 d), absence factor 1, so -1. 87 commits in 90 d = scout. | 2026-11-21 (Upkeep only) | 2027-02-19 |
| dgunning/edgartools | market-data | | | | | | | | |
| mortada/fredapi | market-data | | 0 | | | | Day 2: stars 1,675, 0 default-branch commits in 90 d, last push 2026-01-28, latest release v0.5.2 (2024-05-05); Scorecard API 404 (scout 2026-11-19). Dependents not pulled. **Upkeep 0 (Day 3, `chablis/upkeep.py`, 2026-11-21):** L1 last human commit 2026-01-28 (297 d); R0 latest v0.5.2 2024-05-05 (930 d), none in 365 d; 0 commits in 180 d, 2 in 365 d from 2 authors (bus not scored, n<20). 0 commits in 90 d = scout. | 2026-11-21 (Upkeep only) | 2027-02-19 |
| databento/databento-python | market-data | | | | | | | | |
| alpacahq/alpaca-py | market-data | | | | | | | | |
| polygon-io/client-python | market-data | | | | | | Polygon.io renamed Massive 2025-10-30; client repo may have moved | | |

## Rejected

| Tool | Why | Date |
|---|---|---|
