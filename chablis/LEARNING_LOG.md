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
