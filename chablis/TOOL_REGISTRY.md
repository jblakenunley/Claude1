# Chablis tool registry

Every GitHub tool, library or Action vetted for a 1+Claude system. Scored with
the rubric in `DOCTRINE.md` §6 (Adoption, Upkeep, Security, Fit; 0–3 each).
Entries are `structural` class: review within ~90 days or they lapse to STALE.

No score is written without the evidence behind it. A blank score means not
yet scored, not zero.

## In use

| Tool | Where | Adoption | Upkeep | Security | Fit | Hard stop | Pin | Evidence | Scored | Review by |
|---|---|---|---|---|---|---|---|---|---|---|
| actions/checkout | morning-brief-data.yml (×2) | | 1 | | | | **tag `@v4`, not SHA** — resolves today to `11d5960` (= v4.4.0) | `scout.py pins` 2026-11-18; `git ls-remote` tag `v4` = `v4.4.0`, 2026-11-19. **Upkeep 1 (Day 3, `chablis/upkeep.py`, git history as of 2026-11-21; tool score, same on every checkout row):** L1 last human commit 2026-07-20 (124 d); R2 latest v7.0.1 2026-07-17 (127 d), 6 release days in 365 d, among them tags for v2.8.0, v3.7.0, v4.4.0 and v6.1.0 on 2026-07-16 (commit message "backport fixes to releases-vN"); 0 commits in 90 d (scout 0; Scorecard Maintained 0); scout `pushed_at` 2026-10-17 is dependabot branches; 17 human commits of 31 in 365 d, 3 authors, bus not scored (n<20). Band-failure candidate for Day 7. **Issue health, evidence only, not scored (Day 4, `chablis/issues.py`, issue search, 2026-11-22):** issues open 553 / closed 585 (plus 149 open PRs); cohort created 2026-05-26..08-24, n=28: 61% no comment, 61% closed within 30 d, median 0.9 d to close. **Scorecard, evidence only, not scored (Day 5, scout 2026-11-22; record dated 2026-11-16, 6 d old):** overall 5.8, 14 of 19 checks, no Vulnerabilities check in the record. Marked for weight: Dangerous-Workflow 10, Token-Permissions 0, Pinned-Dependencies 3, Binary-Artifacts 10, Code-Review 10, Branch-Protection 5. Signed-Releases -1; Maintained 0 (not used, `DOCTRINE.md` §6 Day 5 note). | 2026-11-21 (Upkeep only) | 2027-02-19 |
| actions/checkout | chablis-scout.yml, chablis-feed.yml (×2 each) | | 1 | | | | SHA `11d5960a…` (v4.4.0), lightweight tag so tag SHA = commit SHA | `git ls-remote`, 2026-11-18, re-verified 2026-11-19. Upkeep and Scorecard: as the `morning-brief-data.yml` row (Day 3, Day 5). | 2026-11-21 (Upkeep only) | 2027-02-19 |
| actions/checkout | chablis-keyed.yml (branch `chablis-keyed-setup`, not on main); chablis-probe.yml (commit `6051d73`, no live branch) | | 1 | | | | **tag `@v4`, not SHA** | Actions API workflow list + file read at run SHAs, 2026-11-19; invisible to `scout.py pins` Upkeep and Scorecard: as the `morning-brief-data.yml` row (Day 3, Day 5). | 2026-11-21 (Upkeep only) | 2027-02-19 |
| actions/setup-python | morning-brief-data.yml | | 3 | | | | **tag `@v5`, not SHA** — resolves today to `a26af69` (= v5.6.0) | `scout.py pins` 2026-11-18; `git ls-remote` tag `v5` = `v5.6.0`, 2026-11-19. **Upkeep 3 (Day 3, `chablis/upkeep.py`, 2026-11-21; tool score, same on every setup-python row):** L3 last human commit 2026-11-19; R3 v7.1.0 2026-10-21, 5 release days in 365 d; 17 commits in 90 d but 14 are dependabot (3 human); 23 human commits in 365 d, 12 authors, absence factor 3, no deduction. **Issue health, evidence only, not scored (Day 4, `chablis/issues.py`, issue search, 2026-11-22):** issues open 37 / closed 699; cohort n=8 (too few to read): 0% no comment, 50% closed within 30 d. **Scorecard, evidence only, not scored (Day 5, scout 2026-11-22; record dated 2026-11-16, 6 d old):** overall 6.6, 14 of 19 checks, no Vulnerabilities check in the record. Marked for weight: Dangerous-Workflow 10, Token-Permissions 0, Pinned-Dependencies 7, Binary-Artifacts 10, Code-Review 10, Branch-Protection 0. Signed-Releases -1; Maintained 10 (not used, `DOCTRINE.md` §6 Day 5 note). | 2026-11-21 (Upkeep only) | 2027-02-19 |
| actions/setup-python | chablis-scout.yml, chablis-feed.yml | | 3 | | | | SHA `a26af69b…` (v5.6.0), lightweight tag | `git ls-remote`, 2026-11-18, re-verified 2026-11-19. Upkeep and Scorecard: as the `morning-brief-data.yml` row (Day 3, Day 5). | 2026-11-21 (Upkeep only) | 2027-02-19 |
| actions/setup-python | chablis-keyed.yml, chablis-probe.yml (side branches, as above) | | 3 | | | | **tag `@v5`, not SHA** | as above, 2026-11-19. Upkeep and Scorecard: as the `morning-brief-data.yml` row (Day 3, Day 5). | 2026-11-21 (Upkeep only) | 2027-02-19 |

Day 1 (2026-11-19) verified pins and where each Action is used; no dimension was
scored, because the 0–3 bands are not defined until Days 3–7. Newer majors exist
upstream (checkout v6.1.0, setup-python v6.3.0 per `git ls-remote`, 2026-11-19);
whether to move is a Fit question for Day 9. Security is unscored: the Scorecard API
could not be fetched in the 2026-11-19 run and the scout branch was empty.

Day 3 (2026-11-21) scored Upkeep only, with `chablis/upkeep.py` (bands in `DOCTRINE.md` §6); Adoption, Security and Fit stay blank. Correction to the Day 1 paragraph above: newer majors than v6.1.0 and v6.3.0 exist. `git ls-remote --tags`, 2026-11-21: checkout `v7` = `v7.0.1` = `3d3c42e5…` (2026-07-17), setup-python `v7` = `v7.1.0` = `6d4fd22b…` (2026-10-21), both lightweight tags, so tag SHA = commit SHA. The pins above still hold: checkout `v4` = `v4.4.0` = `11d5960a…` (a backport commit tagged 2026-07-16) and setup-python `v5` = `v5.6.0` = `a26af69b…`.

Day 4 (2026-11-22) scored nothing. Issue health is recorded as evidence on seven rows (checkout, setup-python, scrapy, duckdb, OpenBB, yfinance, fredapi) and is not a scored dimension (`DOCTRINE.md` §6 note). The scout 2026-11-21 now carries `dependents` (20 of 20 expected repos); Adoption bands are not defined yet, so Adoption stays blank.

Day 5 (2026-11-23) scored nothing. Scorecard is recorded as evidence on the tools above that have a record or lack one; Security stays blank until bands exist (Day 7). The overall is a risk-weighted mean (Critical 10, High 7.5, Medium 5, Low 2.5) over the checks present, -1 dropped, so each row's per-check values let Chablis recompute any weighting. Which checks to weight is in `DOCTRINE.md` §6 (Day 5 note).

Day 6 (2026-11-24) scored nothing. License is recorded as evidence for all 28 watchlist repos in the License evidence table below (the file read at each commit, by posture); the Hard stop column stays blank because a hard stop is tested at a named posture (`DOCTRINE.md` §6 Day 6 note). checkout and setup-python are MIT.

## Candidates

Watchlist in `watchlist.json`; the nightly scout pulls their signals. Scored
by the learning path, week 1 onward.

Day 3 (2026-11-21) scored Upkeep for scrapy, duckdb, yfinance, fredapi and OpenBB (rows below). Day 2 (2026-11-20) scored nothing. Adoption is scored from dependents, and none were
obtained: WebFetch was refused for `api.deps.dev` and `github.com/*/network/dependents`
(PROVENANCE_REQUIRED, unanswered permission request) and `scout.py` collects no dependents
(queue #14). Stars, forks and contributors are recorded in the Evidence column for the
five tools above and are not a substitute. Scout Scorecard coverage on 2026-11-19: 16 of
28 repos; 404 for 10, 406 for 2.

Day 5 (2026-11-23): scored nothing. Scorecard coverage from the scheduled scout (`main`'s `scout.py`) is 17 of 28 on 2026-11-22. The API returned no record on any of the four days 2026-11-19..22 for nine candidates: duckdb/duckdb, gitleaks/gitleaks, OpenBB-finance/OpenBB, dgunning/edgartools, alpacahq/alpaca-py, anthropics/claude-code-action, apify/crawlee-python, dlt-hub/dlt, meltano/meltano (HTTP 404 every day, except alpaca-py's 406 on 2026-11-19); deps.dev's project record had none for eight of them (alpaca-py: deps.dev 404). recordlinkage and fredapi are 404 at the API and covered only by the deps.dev route (2026-11-21, dated 2026-08-24). Candidate rows below are not annotated; the per-check values are in the scout files on `chablis-scout`.

Day 6 (2026-11-24): scored nothing. License evidence for all 28 is in the table below the candidates; the rows for airbyte, trufflehog, amass and dlt carry a one-line pointer, duckdb and OpenBB an addendum.

| Tool | Category | Adoption | Upkeep | Security | Fit | Hard stop | Evidence | Scored | Review by |
|---|---|---|---|---|---|---|---|---|---|
| scrapy/scrapy | crawling | | 2 | | | | Day 2: stars 65,499, 381 default-branch commits in 90 d, Scorecard 7.1 (scout 2026-11-19; search re-read 2026-11-20: 65,508 stars). Dependents not pulled. **Upkeep 2 (Day 3, `chablis/upkeep.py`, git history as of 2026-11-21):** L3 last human commit 2026-11-19; R3 latest 2.20.0 on 2026-11-06, 11 release days in 365 d; bus: top author made 52% of 825 human commits in 365 d (56% of 375 in 90 d), top two 85% / 91%, absence factor 1, so -1. 381 commits in 90 d = scout 381 = `search/commits` 381. **Issue health, evidence only, not scored (Day 4, `chablis/issues.py`, issue search, 2026-11-22):** issues open 98 / closed 3,227 (scout `open_issues` 171 = 98 + 73 open PRs); cohort n=36: 28% no comment, 53% closed within 30 d, median 7.9 d to close. In 90 d 176 issues closed vs 27 opened; 81 of the latest 100 closures were filed before 2026. **Scorecard, evidence only, not scored (Day 5, scout 2026-11-22; record dated 2026-11-09, 13 d old):** overall 7.1, 14 of 19 checks, no Vulnerabilities check in the record. Marked for weight: Dangerous-Workflow 10, Token-Permissions 10, Pinned-Dependencies 9, Binary-Artifacts 10, Code-Review 7, Branch-Protection 0. Signed-Releases -1; Maintained 10 (not used, `DOCTRINE.md` §6 Day 5 note). | 2026-11-21 (Upkeep only) | 2027-02-19 |
| apify/crawlee-python | crawling | | | | | | | | |
| dlt-hub/dlt | elt | | | | | | **License, evidence only (Day 6, 2026-11-24):** root `LICENSE.txt` Apache-2.0 (commit f5ddcc7). `docs/website/docs/hub/license.md` is the dltHub License: use of the Licensed Materials only with dltHub Services under an Agreement; which files it governs was not read. See the License evidence table. | | |
| meltano/meltano | elt | | | | | | | | |
| airbytehq/airbyte | elt | | | | | | **License, evidence only (Day 6, 2026-11-24):** root `LICENSE` is Elastic License 2.0 (commit 6f91f87); GitHub detector NOASSERTION. Airbyte's README says everything in its public repos except airbyte-protocol (MIT) is ELv2, and Cloud, Enterprise and Agents need a commercial license. ELv2 bars providing the software to third parties as a hosted or managed service and circumventing its license key; Airbyte's FAQ: "You can use software under ELv2 for your commercial business, you simply can't offer it as a managed service" and "Sell a product that directly exposes Airbyte's UI or API" is not allowed. Stops at S and H; clear at U. See the License evidence table. | | |
| duckdb/duckdb | ledger-engine | | 3 | | | | Day 2: stars 43,190, 11,889 default-branch commits in 90 d, MIT; Scorecard API 404 (scout 2026-11-19). Dependents not pulled. **Upkeep 3 (Day 3, `chablis/upkeep.py`, 2026-11-21):** L3 last human commit 2026-11-20; R3 v2.0.1 2026-11-19, 12 release days in 365 d (two lines maintained: v1.4.5 2026-06-14, v1.5.4 2026-06-16); bus: 449 human authors in 365 d, top author 14%, absence factor 9. 12,181 commits in 90 d vs scout 12,188 (2026-11-20). **Issue health, evidence only, not scored (Day 4, `chablis/issues.py`, issue search, 2026-11-22):** issues open 704 / closed 7,572 (plus 569 open PRs); cohort 535 created, newest 500 read: 47% no comment, 60% closed within 30 d, median 8.1 d to close; 837 issues opened in 90 d. **Scorecard, evidence only (Day 5):** API answered 404 on all four scout days 2026-11-19..22; deps.dev project record carries no Scorecard (scout 2026-11-21). No Scorecard overall or checks, so no Security evidence from this route; advisories not sourced either (queue #23, #24). **License, evidence only (Day 6, 2026-11-24):** root `LICENSE` MIT (commit eb31817). 36 nested license files; third_party/mbedtls is Apache-2.0 OR GPL-2.0-or-later, `extension/tpch/dbgen/LICENSE` is the TPC End User License Agreement v2.2. Embedding (V, S) needs the bundle read, not the root. See the License evidence table. | 2026-11-21 (Upkeep only) | 2027-02-19 |
| simonw/sqlite-utils | ledger-engine | | | | | | | | |
| great-expectations/great_expectations | validation | | | | | | | | |
| frictionlessdata/frictionless-py | validation | | | | | | | | |
| moj-analytical-services/splink | entity-resolution | | | | | | | | |
| dedupeio/dedupe | entity-resolution | | | | | | | | |
| J535D165/recordlinkage | entity-resolution | | | | | | | | |
| projectdiscovery/subfinder | recon-passive | | | | | | | | |
| owasp-amass/amass | recon-passive | | | | | | **License, evidence only (Day 6, 2026-11-24):** Apache-2.0 text with a notice line prepended (commit a284d25); GitHub detector NOASSERTION. No stop at any posture from the root file. See the License evidence table. | | |
| gitleaks/gitleaks | secret-scanning | | | | | | | | |
| trufflesecurity/trufflehog | secret-scanning | | | | | | **License, evidence only (Day 6, 2026-11-24):** AGPL-3.0 (commit 22e5133). Clear at U (running it on Blake's own repos conveys nothing); stops at V and S; at H if modified (AGPL-3.0 §13). See the License evidence table. | | |
| ossf/scorecard | supply-chain | | | | | | | | |
| anthropics/claude-code-action | model-powered | | | | | | | | |
| OpenBB-finance/OpenBB | market-data | | 2 | | | | AGPL-3.0 per secondary sources, 2026-11-18, **now superseded**: `LICENSE` is Apache-2.0 on `main` (869cfed1) and `develop` (f0f1852b), last changed by "V5 (#7489)" 2026-09-29 (`git show`, 2026-11-21); GitHub's detector still returns NOASSERTION (scout 2026-11-19; search 2026-11-20). Fit not scored; Apache-2.0 would clear §10 either way. **Identity:** openbb.co/company/open (edit dated 2026-10-01) names OpenBQ, github.com/openbq-org, as steward organization; `git ls-remote` answers HTTP 200 with HEAD f0f1852b for both OpenBB-finance/OpenBB and openbq-org/OpenBB (2026-11-21); `search/repositories` for the old name was 422 on 2026-11-20. The org move is confirmed from OpenBB's own site and the history is identical under both names; which owner GitHub treats as canonical is not (queue #16). Stars 75,602, 26 commits in 90 d (scout 2026-11-20). **Upkeep 2 (Day 3, `chablis/upkeep.py`, 2026-11-21):** L3 last human commit 2026-11-18; R3 `openbb-v5.0.0` 2026-09-29 (per-package tags in one repo: 8 release days in 365 d); bus: top author 58% of 133 human commits in 365 d, absence factor 1, so -1 (factor 2 over 90 d). 26 commits in 90 d = scout. **Issue health, evidence only, not scored (Day 4, `chablis/issues.py`, issue search, 2026-11-22):** read under `openbq-org/OpenBB`; the old owner name is not searchable. Issues open 53 / closed 2,288 (plus 79 open PRs); cohort n=21: 33% no comment, 38% closed within 30 d, median 2.7 d to close. **Scorecard, evidence only (Day 5):** API answered 404 on all four scout days 2026-11-19..22 for `OpenBB-finance/OpenBB`; deps.dev project record carries no Scorecard (scout 2026-11-21); `openbq-org/OpenBB` not queried (queue #16). No Scorecard overall or checks, so no Security evidence from this route; advisories not sourced either (queue #23, #24). **License, re-read (Day 6, 2026-11-24):** root `LICENSE` at f0f1852 is the Apache-2.0 text under a prepended notice ("Copyright (c) 2021-2026 OpenBB Inc."); GitHub detector still NOASSERTION. Superseded: AGPL-3.0 per secondary sources. See the License evidence table. | 2026-11-21 (Upkeep only) | 2027-02-19 |
| ccxt/ccxt | market-data | | | | | | | | |
| ranaroussi/yfinance | market-data | | 2 | | | | Code Apache-2.0; Yahoo data personal use only (Yahoo API terms) — internal use only under §10. Day 2: stars 25,965, 87 default-branch commits in 90 d, Scorecard 5.6 (scout 2026-11-19; search re-read 2026-11-20: 25,968 stars). Dependents not pulled. **Upkeep 2 (Day 3, `chablis/upkeep.py`, 2026-11-21):** L3 last human commit 2026-11-07; R3 1.8.0 2026-11-03, 13 release days in 365 d; bus: top author 54% of 386 human commits in 365 d (55% of 87 in 90 d), absence factor 1, so -1. 87 commits in 90 d = scout. **Issue health, evidence only, not scored (Day 4, `chablis/issues.py`, issue search, 2026-11-22):** issues open 54 / closed 1,679 (plus 59 open PRs); cohort n=25: 8% no comment, 68% closed within 30 d, median 20.8 d to close, 44% of its closures not planned. In 90 d 55 issues closed vs 12 opened; 32 of those 55 were filed before 2026. **Scorecard, evidence only, not scored (Day 5, scout 2026-11-22; record dated 2026-11-09, 13 d old):** overall 5.6, 14 of 19 checks, no Vulnerabilities check in the record. Marked for weight: Dangerous-Workflow 10, Token-Permissions 7, Pinned-Dependencies 5, Binary-Artifacts 10, Code-Review 7, Branch-Protection 0. Signed-Releases -1; Maintained 10 (not used, `DOCTRINE.md` §6 Day 5 note). | 2026-11-21 (Upkeep only) | 2027-02-19 |
| dgunning/edgartools | market-data | | | | | | | | |
| mortada/fredapi | market-data | | 0 | | | | Day 2: stars 1,675, 0 default-branch commits in 90 d, last push 2026-01-28, latest release v0.5.2 (2024-05-05); Scorecard API 404 (scout 2026-11-19). Dependents not pulled. **Upkeep 0 (Day 3, `chablis/upkeep.py`, 2026-11-21):** L1 last human commit 2026-01-28 (297 d); R0 latest v0.5.2 2024-05-05 (930 d), none in 365 d; 0 commits in 180 d, 2 in 365 d from 2 authors (bus not scored, n<20). 0 commits in 90 d = scout. **Issue health, evidence only, not scored (Day 4, `chablis/issues.py`, issue search, 2026-11-22):** issues open 29 / closed 21 (plus 7 open PRs); no issue created since 2026-05-26, so no cohort. **Scorecard, evidence only, not scored (Day 5):** API 404 on all four scout days; the 2026-11-21 scout (PR #19 code, unmerged) read it from the deps.dev project record instead: overall 3.1, record dated 2026-08-24T00:00:00Z (89 d old on 2026-11-21), 14 of 19 checks. Dangerous-Workflow 10, Token-Permissions 0, Pinned-Dependencies 0, Binary-Artifacts 10, Code-Review 3, Branch-Protection 0. Signed-Releases -1; Maintained 0. | 2026-11-21 (Upkeep only) | 2027-02-19 |
| databento/databento-python | market-data | | | | | | | | |
| alpacahq/alpaca-py | market-data | | | | | | | | |
| polygon-io/client-python | market-data | | | | | | Polygon.io renamed Massive 2025-10-30; client repo may have moved | | |

## License evidence (Day 6, 2026-11-24)

Evidence only: no Fit score is written, because Fit has no bands yet (Day 7) and the license is one of its four parts. Each row is the LICENSE file read at the commit shown (treeless `git clone`, root file compared with the SPDX texts in github/choosealicense.com `b851d0a`, 2026-11-20); the detector column is the scout's `license` field, 2026-11-23. "Stops" are the hard stops of `DOCTRINE.md` §6 (Day 6 note) at each posture (U use, V vendor, S ship, H host); a root file does not cover nested or bundled code and no dependency tree was read. Read 2026-11-24; review by 2027-02-22.

| Tool | GitHub detector | LICENSE read | Commit | Stops (root) | Notes |
|---|---|---|---|---|---|
| actions/checkout | MIT | MIT | f548e57 | none from root text |  |
| actions/setup-python | MIT | MIT | 5043d30 | none from root text |  |
| scrapy/scrapy | BSD-3-Clause | BSD-3-Clause | 531bc32 | none from root text |  |
| apify/crawlee-python | Apache-2.0 | Apache-2.0 | 821dd25 | none from root text |  |
| dlt-hub/dlt | Apache-2.0 | Apache-2.0 | f5ddcc7 | root: none; hub docs license: scope not read | Root Apache-2.0; docs/website/docs/hub/license.md is the dltHub License (use only with dltHub Services, all rights reserved). Which files it covers was not read. |
| meltano/meltano | MIT | MIT | 3913352 | none from root text |  |
| airbytehq/airbyte | NOASSERTION | Elastic-2.0 (ELv2) | 6f91f87 | S, H | Repo README (docs/community/licenses): everything in its public repos except airbyte-protocol (MIT) is ELv2; Cloud/Enterprise/Agents are commercial. Root LICENSE_SHORT: "all rights reserved". Stops: S and H when the tool's UI or API is exposed (Airbyte FAQ). |
| duckdb/duckdb | MIT | MIT | eb31817 | root: none; nested: open | 36 nested license files: MIT 17, Apache-2.0 6, BSD-2 2, BSD-3 2, zlib 1, other third_party 7; mbedtls is Apache-2.0 OR GPL-2.0-or-later; extension/tpch/dbgen is the TPC EULA v2.2. Embedding (V, S) needs the bundle read, not the root. |
| simonw/sqlite-utils | Apache-2.0 | Apache-2.0 | 9c66baf | none from root text |  |
| great-expectations/great_expectations | Apache-2.0 | Apache-2.0 | e08d1a8 | none from root text | 6 nested Apache-2.0 (contrib). |
| frictionlessdata/frictionless-py | MIT | MIT | a89290d | none from root text |  |
| moj-analytical-services/splink | MIT | MIT | f319070 | none from root text |  |
| dedupeio/dedupe | MIT | MIT | 3f61e79 | none from root text |  |
| J535D165/recordlinkage | BSD-3-Clause | BSD-3-Clause | b93d976 | none from root text |  |
| projectdiscovery/subfinder | MIT | MIT | adcf761 | none from root text |  |
| owasp-amass/amass | NOASSERTION | Apache-2.0 | a284d25 | none from root text | File is the Apache-2.0 text under a prepended two-line notice (copyright 2017-2026 Jeff Foley, "License: Apache2.0"); detector returned NOASSERTION, cause not confirmed. |
| gitleaks/gitleaks | MIT | MIT | 5f6ec56 | none from root text |  |
| trufflesecurity/trufflehog | AGPL-3.0 | AGPL-3.0 | 22e5133 | V, S (H if modified) | Stops: V, S. H if modified (AGPL §13). U clear. |
| ossf/scorecard | Apache-2.0 | Apache-2.0 | 789a810 | none from root text | Nested matches are source files and test data, not licenses. |
| anthropics/claude-code-action | MIT | MIT | e5c0fcd | none from root text | 1 nested MIT (base-action). |
| OpenBB-finance/OpenBB | NOASSERTION | Apache-2.0 | f0f1852 | none from root text | File is the Apache-2.0 text under a prepended notice (copyright (c) 2021-2026 OpenBB Inc., all files licensed under Apache-2.0); detector returned NOASSERTION, cause not confirmed. 2 nested Apache-2.0. |
| ccxt/ccxt | MIT | MIT | d463867 | none from root text | 7 nested MIT (agent skills). |
| ranaroussi/yfinance | Apache-2.0 | Apache-2.0 | 2492a85 | none from root text |  |
| dgunning/edgartools | MIT | MIT | b9f301c | none from root text |  |
| mortada/fredapi | Apache-2.0 | Apache-2.0 | d0a0ba3 | none from root text |  |
| databento/databento-python | Apache-2.0 | Apache-2.0 | f6529f1 | none from root text |  |
| alpacahq/alpaca-py | Apache-2.0 | Apache-2.0 | d63ecab | none from root text |  |
| polygon-io/client-python | MIT | MIT | 0998686 | none from root text |  |

## Rejected

| Tool | Why | Date |
|---|---|---|
