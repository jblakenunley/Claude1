# Chablis learning log

One entry per lesson, newest at the bottom. Under 300 words. Findings only.

Template:

```
## Day N — <topic> (YYYY-MM-DD, cycle C)
**Exercise:** what was run, against what.
**Findings:** scoped statements with their source.
**Registry:** tools scored or re-scored this lesson.
**Doctrine change:** none | what changed in §6 and why.
**Cost:** tokens if reported; Actions minutes if measured.
```

---

## Day 1 — Pinning (2026-11-19, cycle 1)
**Exercise:** `scout.py pins .github/workflows`, widened to every workflow the Actions API lists, each pin checked upstream via `git ls-remote`. Scout branch empty (0 runs), so signals were gathered directly; the Scorecard API fetch was refused twice (permission timeout), so Security is unscored.
**Findings:**
- `main`: 9 `uses:` lines, all first-party; 6 SHA-pinned (feed, scout), 3 tag-pinned (`morning-brief-data.yml`: checkout@v4 ×2, setup-python@v5).
- Audit gap: Actions lists 5 workflows, `main` holds 3. `chablis-keyed` (passes secrets to a step, `contents: write`) and `chablis-probe` exist only on a side branch or old commits and pin 4 more uses by tag, invisible to the audit: 13 uses, 7 by tag. Branch `chablis-keyed-trigger-001` is still there: its run failed; the two successful runs deleted theirs.
- Registry pins confirmed: checkout `11d5960` = v4.4.0, setup-python `a26af69` = v5.6.0 (`git ls-remote`). Floating `v4`/`v5` resolve to those commits today; newer majors exist.
- A moved tag runs before the secret-bearing step, beside the write token checkout persists (the workflow's own `git push` relies on it). In CVE-2025-30066 tags were retroactively repointed at one commit and the payload printed runner-memory secrets to logs ([advisory mirror](https://cve.circl.lu/vuln/ghsa-mrrh-fwg8-r2c3); [Wiz](https://threats.wiz.io/all-incidents/tj-actionschanged-files-supply-chain-attack)). Neither source reports a first-party tag compromise.
- GitHub can enforce SHA pins; unpinned `uses:` fail ([changelog 2025-08-15](https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/)).
- Schedule lag: all 12 scheduled runs among the latest 30 `morning-brief-data` runs fired 5.4–10.0 h after cron. The scout (09:17Z) and feed (10:41Z) crons cannot precede an 11:53Z lesson.
**Feed load:** none. `chablis-feed` holds no output (0 runs); 0 rows; Drive ledger reachable, unchanged.
**Registry:** pins and evidence updated, 2 side-branch rows added, `chablis-feed.yml` added to Where; no scores (bands undefined until Day 3).
**Doctrine change:** §6 and §10 dated notes.
**Cost:** tokens not reported.

## Day 2 — Adoption vs attention (2026-11-20, cycle 1)
**Exercise:** dependents against stars for scrapy, duckdb, OpenBB, yfinance, fredapi. Scout 2026-11-19 gave the attention side; GitHub search re-read stars 2026-11-20.
**Findings:**
- Dependents not obtained, so no gap is named. WebFetch refused all 15 attempts (10 `api.deps.dev`, 5 `github.com/*/network/dependents`): PROVENANCE_REQUIRED, permission request unanswered, as with Day 1's Scorecard fetch. No curl or Python fallback once WebFetch refused. Scoped to this run's WebFetch, not to deps.dev.
- `scout.py` carries no adoption signal (0 hits for deps.dev or dependents): stars, forks, issues, commits, contributors, Scorecard only.
- Attention, stars / forks / contributors / commits in 90 d (scout): scrapy 65,499 / 12,162 / 763 / 381; duckdb 43,190 / 4,224 / 1,005 / 11,889; OpenBB 75,567 / 7,905 / 280 / 26; yfinance 25,965 / 3,502 / 202 / 87; fredapi 1,675 / 242 / 10 / 0. Search re-read: stars within 0.05% of scout.
- Identity: `repo:OpenBB-finance/OpenBB` returns 422; the 75.6k-star repo (created 2020-12-20, not a fork, homepage openbb.co) is listed under owner `openbq-org`. Move unconfirmed (queue #16). Its GitHub licence is NOASSERTION, so AGPL-3.0 is still unconfirmed.
- Scout Scorecard: 16 of 28 present; 404 for 10 (incl. duckdb, fredapi, OpenBB), 406 for 2. Cause undetermined.
**Feed load:** 11,866 rows from feed 2026-11-19 (UST 294, FRED 3,987, CFTC 7,585, SEC 0). SEC-EDGAR failed: NVDA submissions and facts HTTP 403 on the workflow's fallback User-Agent (repo variable `SEC_USER_AGENT` unset, queue #3; cause not confirmed). Drive `update_file` cannot write content: ledger saved as a new dated file in the private folder, canonical unchanged (queue #15).
**Registry:** no scores; evidence added for the five and OpenBB.
**Doctrine change:** §6 dated note: Adoption stays blank without dependents; resolve canonical repo name first.
**Cost:** tokens not reported; fetch subagents 20.5k.

## Day 3 — Upkeep (2026-11-21, cycle 1)
**Exercise:** Defined the Upkeep bands and ran them on scrapy, duckdb, OpenBB, yfinance, fredapi, plus checkout and setup-python, from treeless git clones (`chablis/upkeep.py`). Scout 2026-11-20 was current (11 of 28 repos with errors). Git was the route: the GitHub API is denied here for out-of-scope repos.
**Findings:**
- Scores as of 2026-11-21: duckdb 3, setup-python 3, scrapy 2, yfinance 2, OpenBB 2, checkout 1, fredapi 0.
- 90-day commits from git match the scout for 7 of 7 (scrapy also `search/commits`, 381). The scout counts bots: 14 of setup-python's 17.
- Bus factor: scrapy's top author made 52% of the year's human commits, the top two 85%; yfinance's top author 54%; duckdb needs 9 people for half. fredapi: 2 commits in 365 d, last release 2024-05-05.
- checkout: last human commit 2026-07-20, but v2.8.0, v3.7.0, v4.4.0, v6.1.0 were tagged 2026-07-16 and v7.0.1 on 07-17. Scout `pushed_at` 2026-10-17 is dependabot branches. Day 1 named v6.1.0 and v6.3.0 as the newer majors; checkout v7.0.1 and setup-python v7.1.0 are newer (`git ls-remote`).
- OpenBB: openbb.co names openbq-org its steward (edit 2026-10-01); both owner names serve HEAD f0f1852b. `LICENSE` is Apache-2.0 on `main` and `develop`, not AGPL. A WebFetch of the raw README said AGPLv3, contradicting git; not used.
- WebFetch worked on 4 of 4 URLs a WebSearch had just returned. Day 1–2 refusals were on URLs from no search; cause untested.
**Feed load:** 9,986 rows read, 24 new (Treasury +14, FRED +10), ledger 11,890. SEC-EDGAR failed: NVDA HTTP 403, as 2026-11-19. `update_file` cannot write content, so saved as `ledger-2026-11-21.db` (queue #15).
**Registry:** Upkeep scored for 7 tools; Day 1 majors corrected; OpenBB licence and owner updated.
**Doctrine change:** §6 Upkeep bands v1; §10 ledger-continuity note.
**Cost:** tokens not reported; fetch subagent 36.4k.

## Day 4 — Issue health (2026-11-22, cycle 1)
**Exercise:** Open/closed counts and a creation cohort for seven tools (scrapy, duckdb, OpenBB, yfinance, fredapi, checkout, setup-python) from GitHub issue search, `chablis/issues.py`. Scout 2026-11-21 was current (now with `upkeep`, `dependents`).
**Findings:**
- The scout's `open_issues` includes PRs ([GitHub docs](https://docs.github.com/en/rest/issues/issues)): scrapy 171 = 98 issues + 73 PRs. 5 of 7 reconcile exactly; duckdb (+7) and yfinance (+1) differ by a snapshot gap.
- Open share of all issues filed: checkout 48.6% and fredapi 58%, against 2.3–8.5% for the other five.
- Time to close among recent closures is sweep-driven: scrapy median 1,985 d (81 of its latest 100 filed before 2026), yfinance 524 d (32 of 55). Not response.
- Cohort (created 2026-05-26..08-24), n / no comment / closed ≤30 d: duckdb 500 of 535 / 47% / 60%; scrapy 36 / 28% / 53%; checkout 28 / 61% / 61%; yfinance 25 / 8% / 68%; OpenBB 21 / 33% / 38%; setup-python 8 / 0% / 50%; fredapi 0. Checkout (Upkeep 1) matches duckdb (3) on speed: not Upkeep restated.
- Median first response not obtained: search has no comment timestamps; CHAOSS excludes bot replies ([source](https://chaoss.community/kb/metric-time-to-first-response/)), `comments:0` does not.
- Scorecard Maintained already counts issue activity (ossf/scorecard, 2026-11-21: "17 issue activity" in 90 days).
**Feed load:** 11,874 rows read from feed 2026-11-21, 1,913 new (CFTC 1,890, Treasury 14, FRED 9), ledger 13,803. SEC-EDGAR failed: NVDA HTTP 403. CFTC's 5,705 rows on 11-20 was the lookback passing one report week, not loss. **Not saved:** the 3.5 MB ledger exceeds the connector's per-call cap (~3.1 MB); `ledger-2026-11-21.db` stays newest (queue #15).
**Registry:** issue evidence on 7 rows; no scores.
**Doctrine change:** §6 note: issue health is evidence only, no scored line.
**Cost:** tokens not reported; fetch subagent 38.0k.

## Day 5 — OpenSSF Scorecard (2026-11-23, cycle 1)
**Exercise:** Read the 19 documented checks, tested the score formula on the scout's per-check data (2026-11-22, `main`'s `scout.py`: 17 of 28 repos with a record), and marked which checks Chablis weights. Risk levels came from the [pkg.go.dev table](https://beta.pkg.go.dev/github.com/ossf/scorecard/v5), read verbatim; two API records read directly.
**Findings:**
- Risk-weighted mean (10 / 7.5 / 5 / 2.5), -1 dropped, reproduces 19 of 19 reported scores within 0.05, deps.dev-sourced records included. The pages do not state the -1 rule; the data does.
- The 16 weekly-scan API records carry 14 checks, without Vulnerabilities, Dependency-Update-Tool, CI-Tests or Contributors; [cve-bin-tool](https://api.securityscorecards.dev/projects/github.com/intel/cve-bin-tool) and [secure-repo](https://api.securityscorecards.dev/projects/github.com/step-security/secure-repo) carry 18. The README (model-extracted summary) says three are omitted. For those 16 repos Scorecard holds no vulnerability evidence (queue #23).
- Six weighted checks rank the 16 at Spearman 0.76 against the overall: trufflehog 1st→6th, airbyte 10th→16th. CII-Best-Practices is 0 on 16 of 16; Signed-Releases -1 on 12; Dangerous-Workflow 0 on great_expectations and airbyte.
- Nine of 28 repos had no API record on four days. The 11-21 scout's 19 came from PR #19's code (unmerged); fredapi and recordlinkage's deps.dev records were 89 d old, the API's 6–27 d.
- Fetch: 6 of 6 URLs a search returned verbatim loaded; 5 others were refused (queue #17).
**Feed load:** feeds 11-21 and 11-22 into the 11-21 ledger: 1,913 new rows (CFTC 1,890, Treasury 14, FRED 9); 11-22 added 0; ledger 13,803. SEC-EDGAR failed: NVDA HTTP 403. Saved gzipped (329 KB; the 3.5 MB .db exceeds the upload cap) as `ledger-2026-11-23.db.gz`.
**Registry:** Scorecard evidence on 7 rows; no scores.
**Doctrine change:** §6 Scorecard checks v1; §10 gzipped-ledger note.
**Cost:** tokens not reported; fetch subagents 105.8k.

## Day 6 — License fit (2026-11-24, cycle 1)
**Exercise:** Read the LICENSE file at HEAD of all 28 watchlist repos (treeless clones), compared each with the SPDX texts in github/choosealicense.com (`b851d0a`), read nested license files where a repo has several, and checked clause wording against the texts and vendor FAQs. Scout 2026-11-23 was current.
**Findings:**
- The exercise calls this repo's LICENSE proprietary; the file is Apache-2.0 (initial commit `0cc6d85`, 2026-08-12; same text as `licenses/LICENSE-APACHE-2.0`). Blake's shipped products are proprietary, so the stops are written by posture: use, vendor, ship, host.
- 28 of 28 resolve from the file: MIT 13, Apache-2.0 11, BSD-3-Clause 2, AGPL-3.0 1 (trufflehog), ELv2 1 (airbyte). GitHub's field said NOASSERTION for airbyte, amass and OpenBB; amass and OpenBB are Apache-2.0 under a prepended notice.
- A root file is not the tree: duckdb has 36 nested files (mbedtls Apache-2.0 OR GPL-2.0-or-later; the TPC EULA); dlt's docs carry the dltHub License; Airbyte's README says all but airbyte-protocol (MIT) is ELv2.
- No tool stops at use. Trufflehog stops at vendor and ship (and host if modified, AGPL §13); airbyte at ship and host where its UI or API is exposed.
- Not used: GPL FAQ entries #UnreleasedMods and the AGPL one were read only as a summary, not verbatim.
- Fetch: 7 of 7 URLs a search returned loaded.
**Feed load:** 11,850 rows read (feed 2026-11-23), 24 new (Treasury 14, FRED 10), ledger 13,827; saved `ledger-2026-11-24.db.gz` (329,483 B). SEC-EDGAR failed: NVDA submissions and facts HTTP 403 (queue #3).
**Registry:** license evidence for 28 repos; no scores (Fit bands wait for Day 7).
**Doctrine change:** §6 Day 6 note, hard stops by posture.
**Cost:** tokens not reported; fetch subagents 84.4k.

## Day 7 — Rubric v1 review (2026-11-25, cycle 1)
**Exercise:** Scored the first ten watchlist tools on all four dimensions: Upkeep re-run from git (as of 2026-11-25), Scorecard from scout 2026-11-24 (current; 13 of 28 repos with errors), dependents from scout 2026-11-21 (the newest carrying them), runtime dependencies from each pyproject.
**Findings:**
- Adoption, Security and Fit had no bands; v1.1 sets them (`DOCTRINE.md` §6). Four scores exist for 3 of 10 (scrapy, sqlite-utils, great_expectations); none enters, since advisories are unsourced.
- Adoption is blank for 3: deps.dev dependents cover npm, Cargo, Maven and PyPI only ([docs](https://docs.deps.dev/api/v3alpha/index.html)), so Actions and airbyte have none. Code search counts workflow files (checkout 9,764,864; setup-python 1,507,328), a different measure.
- Day 2's gap: sqlite-utils is 7th of 7 by stars (2,228) and 2nd by dependents (760); scrapy is 1st (65,562) and 3rd (552). Spearman 0.29, n=7.
- Security is blank for 4 (crawlee, dlt, meltano, duckdb: 404 on 6 of 6 days). great_expectations' record stopped being served after 11-22. Six-check scores run 3.83 to 7.72; Token-Permissions is 0 on 5 of 6.
- Upkeep failed on airbyte: R0 (no tag since 2025-10-15) beside 656 human commits in 90 d, so L3 with R0 is now unscored. Four of ten sit within 7 points of the 50% bus line; kept.
- duckdb's PyPI package is built from duckdb/duckdb-python.
- Main's scout lost `dependents` and `upkeep` after 11-21 (PR #19 open).
- Fetch: 3 of 3 search-returned URLs loaded.
**Feed load:** feed 2026-11-24: 11,866 rows read, 17 new (Treasury 14, FRED 3), ledger 13,844; SEC-EDGAR failed (NVDA HTTP 403, queue #3). Saved as `ledger-2026-11-25.db.gz`.
**Registry:** ten tools scored; table added.
**Doctrine change:** §6 rubric v1.1; `upkeep.py` emits null for L3 with R0.
**Cost:** tokens not reported; fetch subagents 87.0k.

## Day 8 — Permissions (2026-11-26, cycle 1)
**Exercise:** Audited `permissions:` in all 5 registered workflows (11 file versions, 23 of 27 branches), read effective scope from the three 2026-11-25 job logs, and traced each write to a command. Scout 2026-11-25 was current (14 of 28 repos with errors).
**Findings:**
- All 11 versions grant only `contents: write`, workflow-wide; none has a job block; each is one job. None triggers on pull request, issue or comment events.
- Feed, scout and morning-brief ran with `Contents: write`, `Metadata: read`.
- Only pushes need the write: feed to `chablis-feed`; scout to `chablis-scout`; morning-brief to `mb-data` plus trigger-branch delete; side-branch keyed and probe to `chablis-data` plus delete. setup-python, fetch and probe steps need no write. Read from commands, not run with less.
- Moving the block to the job changes nothing here; narrowing needs separate read and write jobs.
- setup-python received the token though no workflow passes it ([docs](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token)). checkout stores it in git config unless told not to.
- action.yml documents no permissions key ([reference](https://docs.github.com/en/actions/reference/workflows-and-actions/metadata-syntax.md)): an Action gets what its job grants.
- Both pinned Actions target Node 20, [removed 2026-09-23](https://github.blog/changelog/2026-09-23-node-20-is-no-longer-available-in-github-actions/), and run on Node 24.
- Fetch: 8 of 8 search-returned URLs loaded. Exposure detail is in the private recon folder.
**Feed load:** feed 2026-11-25: 11,877 rows read, 12 new (FRED), ledger 13,856; SEC-EDGAR failed (NVDA HTTP 403, queue #3). Saved `ledger-2026-11-26.db.gz`, hash verified.
**Registry:** checkout, setup-python: job hard stop and runtime evidence; scores unchanged.
**Doctrine change:** §6 rubric v1.2: job test added to the write hard stop.
**Cost:** tokens not reported; fetch subagents 126.0k.
