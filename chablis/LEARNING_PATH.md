# Chablis — daily learning path: GitHub tool quality and selection

One lesson a day, 30 days a cycle. Each lesson = one topic, one exercise run
against a real tool or system, one logged finding, and registry updates for
every tool scored. Weeks 1–2 build the rubric; week 3 applies it to the market
data feed; week 4 covers recon tooling and the discipline of keeping the
registry current.

Rules for every lesson: verify any external fact before logging it; log
findings, not verdicts; record the tokens the lesson cost if the runtime
reports them; recon output goes to the private Drive folder's `recon/`, never this repo.

## Week 1 — Reading a repository's vital signs (Doctrine §6)

| Day | Topic | Exercise |
|---|---|---|
| 1 | Pinning | Run `python3 chablis/scout.py pins .github/workflows` on this repo. Log every Action pinned by tag rather than SHA and what a moved tag could do. |
| 2 | Adoption vs attention | For five watchlist tools, pull dependents from deps.dev and compare with stars. Name the biggest gap. |
| 3 | Upkeep | Commit cadence, release cadence, bus factor for the same five. Define the 0–3 bands. |
| 4 | Issue health | Open-vs-closed issue ratio and median response time; decide whether it earns a rubric line. |
| 5 | OpenSSF Scorecard | Read every Scorecard check; mark which ones Chablis should weight and why. |
| 6 | License fit | Map common licenses against this repo's proprietary LICENSE. Write the hard-stop list. |
| 7 | Rubric v1 review | Score the first ten watchlist tools end to end; amend §6 where the bands failed. |

## Week 2 — GitHub Actions supply chain

| Day | Topic | Exercise |
|---|---|---|
| 8 | Permissions | Audit `permissions:` in every workflow in this repo. Justify each write. |
| 9 | Third-party Actions | First-party vs verified vs unverified: score every Action the repos use. |
| 10 | Secrets in workflows | Review how `CDOT_API_KEY` is guarded in morning-brief; generalize the pattern. |
| 11 | Keeping pins current | Dependabot vs Renovate for SHA-pinned Actions; recommend one with cost. |
| 12 | Workflow injection | `pull_request_target`, untrusted input in `run:`. Check both repos. |
| 13 | Actions cost | Measure the scout's run time; verify current GitHub minutes terms for private repos; cite them. |
| 14 | Actions policy | Write the house Actions policy for both repos into §6. |

## Week 3 — The market data feed (Doctrine §10)

| Day | Topic | Exercise |
|---|---|---|
| 15 | Feed health | Read the last week of `chablis-feed` manifests: rows per source, errors, gaps. Fix the worst one. |
| 16 | EDGAR | Score edgartools against `feed.py`'s stdlib SEC adapter; adopt it if it wins. Add full-text search and 13F holdings as candidate sources. |
| 17 | Macro | Score fredapi; decide whether vintages (ALFRED) belong in the feed for revision-sensitive series. |
| 18 | Crypto | Score ccxt; map which exchanges' public endpoints carry usable terms for internal use. |
| 19 | Equities, free tier | Measure yfinance reliability for a week (errors, gaps, adjustment differences vs Massive's free plan). Log both sides. |
| 20 | Vendors | Massive vs Databento vs Alpaca vs Tiingo: coverage, history, price for internal use — every side verified and cited. |
| 21 | Identifiers | CIK ↔ ticker ↔ FIGI ↔ LEI: build the security master the feed joins on; score the open libraries for it. |

## Week 4 — Recon tooling and registry discipline

| Day | Topic | Exercise |
|---|---|---|
| 22 | Passive subdomain discovery | Score subfinder and amass (passive modes only); run against a domain Blake owns. Output to Drive `recon/`. |
| 23 | Certificate transparency | Compare crt.sh with one alternative on the same owned domain. |
| 24 | Secret scanning | gitleaks vs trufflehog: score both, scan this repo's history, findings to Drive `recon/`. |
| 25 | SBOM and dependency graph | Generate an SBOM for this repo; note what it reveals. |
| 26 | Abandonment | Archived repos and community forks: when does a fork become the real project? |
| 27 | Model-powered tools | claude-code-action, Copilot: permissions and current pricing, verified and cited. |
| 28 | Prompt injection | Where untrusted repo content (READMEs, issues) reaches Chablis; name the boundary. |
| 29 | Registry hygiene | Expire stale entries by TTL; re-score anything past review date. |
| 30 | Cycle close | Rubric v2, the top-ten registry, and what changed in how Chablis chooses. |
