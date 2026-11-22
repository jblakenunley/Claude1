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
