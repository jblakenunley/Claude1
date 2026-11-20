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
**Feed load:** 11,866 rows from feed 2026-11-19 (UST 294, FRED 3,987, CFTC 7,585, SEC 0). SEC-EDGAR failed: NVDA submissions and facts HTTP 403 (`SEC_USER_AGENT` unset, queue #3; cause not confirmed). Drive `update_file` cannot write content: ledger saved as a new dated file in the private folder, canonical unchanged (queue #15).
**Registry:** no scores; evidence added for the five and OpenBB.
**Doctrine change:** §6 dated note: Adoption stays blank without dependents; resolve canonical repo name first.
**Cost:** tokens not reported; fetch subagents 20.5k.
