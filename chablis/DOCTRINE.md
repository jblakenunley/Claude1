# Chablis doctrine

The overarching instructions for Chablis. Section 6, the tool rubric, is
amended by the daily learning path. Every amendment is dated and traced to a
log entry.

---

## 1. What Chablis is measured on

1. **Is it the right data** — the correct entity, from a source allowed to
   carry what you claim it carries.
2. **Could a stranger trust it from the ledger alone** — every row traceable
   to a source, a retrieval time and a freshness horizon.

A pull that looks finished and is silently partial is a failure, not a draft.
Mark what is missing.

## 2. The authorization gate — before any fetch

Class every target and write the class into the `pull` row before a byte moves:

- **PUBLIC** — public APIs, open-data portals, bulk dumps, public pages and the
  JSON endpoints those pages call. Anything served without a credential.
- **CREDENTIALED** — reached with a key, token or account Blake holds and is
  entitled to use. Record whose and where it came from (`auth_ref`). Secrets
  come from env or keychain, never from code or the ledger.
- **LICENSED** — governed by a data agreement. Record the license and its limits.

A target that fits none of these is out of scope: report it, name what would
bring it in scope (a credential, a license, written test authorization), and
move on. Read `robots.txt` once per host, record `robots_checked_at`, honor it.
Rate limits are a courtesy budget: honor `Retry-After`, back off on 429/503,
cap per-host concurrency.

## 3. The loop — discover, access, transform, load

**Discover.** Rank routes cheapest and cleanest first: official API → bulk
dump → open-data portal (Socrata and CKAN have uniform APIs) → structured feeds
on a page (sitemaps, RSS, JSON-LD, the page's own JSON/GraphQL endpoint) →
compliant scraping of public pages → licensing or a data marketplace. Log the
route chosen and the two rejected, in one line.

**Access.** Paginate to exhaustion and record the last cursor so a run resumes.
Pull incrementally by default (`If-Modified-Since`, ETags, high-watermark).
Idempotent requests, checkpoints, and a dead-letter table for failed records.

**Transform.** Infer and store the schema; flag drift as a finding. Resolve
entities before merging: blocking keys, then similarity, then a decision with
a recorded confidence. A circumstantial match is held until an identifier
agrees; adjacent-identifier search often resolves faster than name search.
Normalize (ISO-8601 UTC dates, consistent nulls). Quarantine failing rows with
a reason.

**Load.** Into the shared ledger, `ledger.db` in the private Drive folder
"Chablis Data (private)" (schema: `chablis/ledger/schema.sql`), landing → staged → curated, with lineage columns
carried to curated so any value can be recomputed, not just cited backward.

## 4. Provenance and freshness

Every atom is stamped at retrieval and given a source class with a
time-to-live. At expiry `_current` flips to 0: binary CURRENT/STALE, no decay.

| Class | Examples | TTL |
|---|---|---|
| `reference` | legal identifiers, historical filings | 365 d+ |
| `structural` | org structure, rosters, catalogs, **tool registry entries** | ~90 d |
| `ecosystem` | partnerships, affiliations | ~30 d |
| `signal` | pricing, hiring, competitive moves | ~7 d or event |
| `realtime` | market and live feeds | intraday / event |

## 5. Evidence discipline

- A negative is a scoped statement about a **source**: "did not surface via X,
  which records only Y." State what the source could have carried; try two
  routes before recording absence.
- Identity before scope: confirm the right entity before trusting a source's
  silence about it.
- No inward-looking verification: corroborate with a second, independent source.
- Roll call, not recall: aggregates are regenerated from records at use.
- Findings, not verdicts.

## 6. Tool rubric — GitHub tool quality and selection

*Amended by the learning path. v1, 2026-11-18; v1.1, 2026-11-25 (Day 7 note); v1.2, 2026-11-26 (Day 8 note); v1.3, 2026-11-27 (Day 9 note).*

Score each dimension 0–3. A tool enters a 1+Claude system only with a recorded
score, the evidence behind each number, and a review date (~90 days).

| Dimension | What it measures | Evidence |
|---|---|---|
| **Adoption** | Real use, not attention | Dependents (deps.dev, GitHub dependency graph). Stars are recorded but never scored — they can be bought |
| **Upkeep** | Will it be here next year | Commits in last 90 days, release cadence, contributors beyond the top one (bus factor), archived flag |
| **Security** | Supply-chain risk | OpenSSF Scorecard (overall and per check), open advisories, signed releases |
| **Fit** | Does it suit this stack | License compatible with a proprietary repo; stdlib-first convention; API stability; model and vendor lock-in |

**Hard stops** — any one blocks adoption regardless of score: archived repo;
unpatched critical advisory; a license that would force disclosure of Blake's
code; an Action that requests, or is given by its job, write permissions it does not need (Day 8 note).

**GitHub Actions rules:**
- Pin every Action, first-party included (Day 9 note), to a full commit SHA,
  with the version in a comment. A tag can be moved; a SHA cannot.
- Grant `permissions:` per job, least privilege. Default to read.
- Never interpolate untrusted input (issue titles, PR bodies, branch names)
  directly into `run:`.
- Publisher tier breaks ties only: first-party, verified-creator and other
  Actions all get the full rubric (Day 9 note).

*Note 2026-11-19 (Day 1, LEARNING_LOG).* (1) Audit every workflow GitHub has
registered for the repo (Actions API `list_workflows`) and every branch or commit
that carries one; `scout.py pins` reads only the checked-out tree and missed two
tag-pinned workflows, one of them secret-bearing. (2) Resolve a tag to its commit
with `git ls-remote <repo> refs/tags/<tag> refs/tags/<tag>^{}` and use the `^{}`
line when present: an annotated tag lists its tag-object SHA first (actions/checkout
`v6.0.3` is one). (3) Open for Days 9 and 14: whether the pin rule covers
first-party `actions/*`. Practice today pins them in `chablis-*.yml` and not in
`morning-brief-data.yml`.

*Note 2026-11-20 (Day 2, LEARNING_LOG).* (1) Adoption is scored from dependents, and none
of the routes tried this run supplied them: `scout.py` collects none, and WebFetch was
refused for `api.deps.dev` and `github.com` in an unattended run (PROVENANCE_REQUIRED). Until
the scout carries dependents, Adoption stays blank, never filled from stars, forks or
contributors. A signal the lesson needs from a host WebFetch refuses belongs in the scout,
which has Actions egress. (2) Resolve a repo's current owner and name before pulling its
signals: `search/repositories` with `repo:<owner>/<name>` returning 422, or a same-name hit
under a different owner, means the watchlist name may be stale (OpenBB today). Hold the score
until a second source confirms the move.

*Note 2026-11-21 (Day 3, LEARNING_LOG).* **Upkeep bands v1**, scored from git history with
`chablis/upkeep.py` (treeless clone; no API quota; scheduled runs are denied GitHub API reads of
repos outside the session scope). Windows end on the scoring date; bots are excluded; authors are
merged by email. **L**, days since the last human commit on the default branch: ≤30 → 3, ≤90 → 2,
≤365 → 1, else 0. **R**, latest full-version release tag and distinct release *days* in 365 d (a
monorepo or a same-day backport counts once): age ≤90 d and ≥4 days → 3; ≤180 d and ≥2 → 2; ≤365 d
→ 1; else 0. **Bus**: the CHAOSS Contributor Absence Factor, the fewest people behind 50% of the
last 365 d of human commits ([CHAOSS](https://www.chaoss.community/kb/metric-contributor-absence-factor/),
page modified 2024-11-07); with ≥20 human commits and a factor of 1, deduct 1. **Upkeep =
max(0, min(L, R) − deduction)**; an archived repo is 0. The scout's `commits_90d` matched git for
7 of 7 repos but counts bots (setup-python: 14 of 17), so score from human counts. Open for Day 7:
(1) a stable first-party Action silent for 90+ days scores low (checkout 1; Scorecard Maintained
is also 0); (2) the 50% line is a cliff (scrapy's top author is 52%, its top two 85%, so factor 1).

*Note 2026-11-22 (Day 4, LEARNING_LOG).* **Issue health v1: evidence only, no scored line.**
(1) Count issues with `is:issue` search (`chablis/issues.py`; search works for repos the session was
not granted, repo-scoped reads do not). The scout's `open_issues` is GitHub's REST count, and the REST
API treats every pull request as an issue ([GitHub docs](https://docs.github.com/en/rest/issues/issues)):
scrapy 171 = 98 issues + 73 PRs; 5 of 7 repos reconcile exactly. Never score from it. (2) Lifetime open
share, closed-in-window flow and time-to-close among recent closures are not read: a sweep of old
issues dominates them (scrapy: 176 closed vs 27 opened in 90 d, median age at close 1,985 d). (3) The
usable read is a creation cohort, issues created in the 90 days before the window so each had 90 days
to resolve: share with no comment, share closed within 30 d, and n. Only duckdb has n of 50 or more; the
other six have 36 or fewer (fredapi 0), where a few issues move a share by 3-5 points, so no band is
set. (4) First-response time is not collected: search returns no comment timestamps, and CHAOSS Time to
First Response excludes bot replies and filters by responder role
([CHAOSS](https://chaoss.community/kb/metric-time-to-first-response/), modified 2024-10-24), while
`comments:0` counts bots. (5) Scorecard's Maintained check already reads issue activity ("30 commit(s)
and 17 issue activity found in the last 90 days", ossf/scorecard, 2026-11-21), so a scored line would
partly double-count. Revisit at Day 5 (each Scorecard check) and Day 7 (rubric v1 review).

*Note 2026-11-23 (Day 5, LEARNING_LOG).* **Scorecard checks v1: read per check; no scored line until Day 7.**
(1) The overall is the risk-weighted mean of the checks present, Critical 10 / High 7.5 / Medium 5 / Low 2.5, over 19
documented checks ([pkg.go.dev](https://beta.pkg.go.dev/github.com/ossf/scorecard/v5), table read verbatim 2026-11-23). The
pages read did not say how -1 is treated; dropping -1 reproduces the reported score for 19 of 19 scout records within 0.05
(2026-11-21; 17 of 17 on 11-22; both deps.dev-sourced records included). Chablis recomputes any weighting from per-check values
at use and never takes the overall as a Security score. (2) The API's weekly records (16 of 16 on 2026-11-22) carry 14 checks,
without Vulnerabilities, Dependency-Update-Tool, CI-Tests or Contributors. Three 18-check records exist: ossf/scorecard in the
scout, cve-bin-tool and secure-repo read directly ([API](https://api.securityscorecards.dev/projects/github.com/step-security/secure-repo),
2026-11-23). The [README](https://github.com/ossf/scorecard), by a model-extracted summary, says the weekly scan omits three,
not four. So for those 16 repos Scorecard says nothing about known vulnerabilities, and the hard stop "unpatched critical
advisory" needs its own source (OSV, the service behind that check per pkg.go.dev, or GitHub advisories): queue #23.
(3) Marks. **Weight** once bands exist: Dangerous-Workflow, Token-Permissions (12 of 16 score 0, so low spread),
Pinned-Dependencies, Binary-Artifacts, Code-Review, Branch-Protection; each is a hazard that reaches the consumer through the
tool's build or release path and is evaluable on most records. Vulnerabilities joins when sourced. **Evidence only:**
Signed-Releases (-1 on 12 of 16, too rarely evaluable to carry a score), Security-Policy, SAST, Fuzzing, Packaging (-1 on 9 of
16), Dependency-Update-Tool, CI-Tests, Contributors. **Not used:** Maintained (duplicates Upkeep), License (Fit, Day 6),
CII-Best-Practices (0 on 16 of 16, no information here). A Dangerous-Workflow of 0 (great_expectations, airbyte on 2026-11-22)
is a prompt to read that repo's workflows, not a hard stop; the hard-stop list is Day 6. (4) The marks change ranks: the six
weighted checks against the overall over the 16 records give Spearman 0.76 (dropping Maintained alone, 0.96); trufflehog
1st→6th, airbyte 10th→16th, great_expectations 9th→15th, yfinance 8th→4th. (5) Freshness and coverage: API records were 6–27 d
old on 2026-11-22; the two deps.dev-sourced records were 89 d old. Nine of 28 watchlist repos had no record on any of four days
(`TOOL_REGISTRY.md`). A tool with no record gets no Scorecard evidence, never a default.

*Note 2026-11-24 (Day 6, LEARNING_LOG).* **License hard stops v1, by posture.** (1) The license is the LICENSE file read at the
scored commit; GitHub's `license` field is a pointer. It returned NOASSERTION for 3 of 28 scout records (2026-11-23), and the files
read as Apache-2.0 (amass, OpenBB: the standard text under a prepended notice) and Elastic License 2.0 (airbyte). All 28 resolve:
MIT 13, Apache-2.0 11, BSD-3-Clause 2, AGPL-3.0 1, ELv2 1. A root file does not cover the tree: duckdb has 36 nested license files
(mbedtls is Apache-2.0 OR GPL-2.0-or-later; the tpch dbgen carries the TPC EULA), dlt's docs carry the dltHub License beside its
Apache-2.0 root, and Airbyte's README says everything in its public repos except airbyte-protocol (MIT) is ELv2. Read the nested
files on the path the tool takes. (2) Every registry entry names its **posture**, and hard stops are tested at it. **U** use: Blake
or his agents run it, nothing is conveyed, no outside users (the §10 boundary). **V** vendor: its code is copied or linked into a
repo of Blake's, either this public one (`LICENSE` is Apache-2.0, since the initial commit 2026-08-12) or a private proprietary one.
**S** ship: it goes to a client or into another surface (Lightning Web Components, a client-installed interface). **H** host:
outside users reach it over a network. (3) **Stops.** *No license text* (all rights reserved, [choosealicense.com](https://choosealicense.com/no-permission/)):
V, S, H, and U until one is found. *GPL-2.0, GPL-3.0, AGPL-3.0*, and LGPL when combined into a shipped work: V and S. GPL-3.0 §0:
"Mere interaction with a user through a computer network, with no transfer of a copy, is not conveying"; §2: "You may make, run
and propagate covered works that you do not convey, without conditions"; the [GPL FAQ](https://www.gnu.org/licenses/gpl-faq):
"an organization can make a modified version and use it internally without ever releasing it outside the organization"
(#GPLRequireSourcePostedPublic) and "You cannot incorporate GPL-covered software in a proprietary system" (#GPLInProprietarySystem).
So U is clear (trufflehog today). AGPL-3.0 §13 adds H: a modified version must offer source to every user interacting with it
remotely. *Use-restricted* licenses stop S and H where the tool's own function is what is exposed: ELv2 bars hosting it as a managed
service for third parties ([Airbyte FAQ](https://docs.airbyte.com/community/licenses/license-faq): "You can use software under ELv2
for your commercial business, you simply can't offer it as a managed service"; "Sell a product that directly exposes Airbyte's UI
or API" is not allowed); SSPL stops H (MongoDB's [FAQ](https://www.mongodb.com/legal/licensing/server-side-public-license/faq):
internal-only service use is not covered); BUSL-1.1 grants non-production use and only the production use its Additional Use Grant
permits, otherwise a commercial license ([SPDX text](https://spdx.org/licenses/BUSL-1.1)), so read each grant; a noncommercial-only
text (PolyForm Noncommercial) stops client work, while U for Blake's own research stays his call under the 2026-11-18 decision.
MIT, BSD, ISC and Apache-2.0 carry notice duties only (Apache-2.0 §3 also ends a patent license if you sue over the Work); MPL-2.0
is file-level (§3.3 allows a Larger Work under terms of your choice). (4) Scope: the rule reads each tool's own license text, no
dependency tree, and is Chablis's operating rule, not legal advice; a close call goes to Blake. Open for Day 7: Fit has no bands yet.

*Note 2026-11-25 (Day 7, LEARNING_LOG).* **Rubric v1.1: bands for Adoption, Security and Fit; one Upkeep change; entry rule.**
(1) **Adoption**: deps.dev `dependentCount` for the package built from the repo, "the number of packages known to depend on this
package version, either directly or indirectly", available for npm, Cargo, Maven and PyPI only, and "indicative of relative popularity
rather than precisely accurate" ([API v3alpha](https://docs.deps.dev/api/v3alpha/index.html)). Decade bands: 1,000 or more 3; 100 to 999
2; 10 to 99 1; under 10 0. A `source_repo_match` of false is a flag to read, not a reason to drop (duckdb's package is built from
duckdb/duckdb-python). Actions and applications have no route: Adoption stays blank, never stars or forks. Code search
(`gh api search/code`, works in lessons) counts workflow files referencing an Action (checkout 9,764,864, setup-python 1,507,328 on
2026-11-25); that is a different measure, evidence only. (2) **Security** (partial until Vulnerabilities is sourced, queue #23): S6 is the
risk-weighted mean of the six Day 5 checks, -1 dropped, weights from the Scorecard risk table ([pkg.go.dev](https://beta.pkg.go.dev/github.com/ossf/scorecard/v5):
Critical 10, High 7.5, Medium 5, Low 2.5): Dangerous-Workflow 10, Token-Permissions 7.5, Pinned-Dependencies 5, Binary-Artifacts 7.5,
Code-Review 7.5, Branch-Protection 7.5 (sum 45). Quarter bands: 7.5 or more 3; 5 to 7.49 2; 2.5 to 4.99 1; under 2.5 0. Scored from the newest record
within 90 d; no record is blank. (3) **Fit** = min(license cap, footprint). License cap, at the registered posture (Day 6): a stop
there is 0 and a hard stop; a stop at a wider posture, or a nested or bundled license that could bind the posture and is unread, is 2;
otherwise 3. Footprint (stdlib-first): unique runtime dependencies the package declares, extras excluded: 5 or fewer 3; 6 to 15 2; 16 to 40 1;
more 0; none for an Action or application. Libraries are registered at V, Actions and servers at U. API stability and lock-in are not scored.
(4) **Upkeep**: L3 with R0 is not scored (live repo, no release tag in 365 d, release channel unread), not 0: airbyte has 656 human commits in
90 d and no tag since v2.0.0 (2025-10-15). `upkeep.py` now emits null. The 50% bus line stays: four of the ten (great_expectations 47.0%, scrapy 52.2%, meltano 54.6%,
checkout 56.2% with n under 20) sit within 7 points of it, and no outcome data exists to place a better one; checkout's 1 stays. Revisit in cycle 2.
(5) **Entry**: a tool enters only with all four dimensions scored, no hard stop, and its advisories checked. A blank blocks entry and is
never 0. No composite is computed: a sum would let Adoption offset a Security 0. Tools in use are re-scored, not removed. (6) The scout
on `main` stopped carrying `dependents` and `upkeep` after 2026-11-21, whose run came from open PR #19 (queue #14, #20): lessons read the
2026-11-21 values and date them.

*Note 2026-11-26 (Day 8, LEARNING_LOG).* **Rubric v1.2: the write-permission hard stop gains a job test.** (1) The
[metadata reference](https://docs.github.com/en/actions/reference/workflows-and-actions/metadata-syntax.md) documents the keys name, author, description, inputs, outputs, runs and branding, none for
permissions, and "An action can access the `GITHUB_TOKEN` through the `github.token` context even if the workflow does not
explicitly pass" it ([GitHub docs](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token); both read 2026-11-26). A job-level block applies to "all actions and run commands
within that job that use the `GITHUB_TOKEN`" ([GHES 3.13 page, discontinued](https://docs.github.com/en/enterprise-server@3.13/actions/how-tos/writing-workflows/choosing-what-your-workflow-does/controlling-permissions-for-github_token)). So v1's stop still covers the writes an
Action's documentation asks for, and adds: an Action runs in a job that holds a write permission only if it takes part in
making that write; the rest belongs in a read job. (2) Audit: parse every workflow version on every branch; read the `GITHUB_TOKEN Permissions` block in a job log (the
effective grant); name the command that needs each write. No command, no write. (3) A layout that passes: one job that fetches
with read, one that only commits with write, `permissions:` on each, and `persist-credentials: false` on every checkout that
does not push. GitHub advises read-only contents as the default, "increased, as required, for individual jobs"
([secure use](https://docs.github.com/en/actions/reference/security/secure-use.md)). (4) Vetting an Action includes the runtime it declares at the pinned SHA: the pin freezes that too.
(5) The three live jobs do not pass today (queue #25); tools in use stay (v1.1 entry rule). Day 14 sets the house policy.

*Note 2026-11-27 (Day 9, LEARNING_LOG).* **Rubric v1.3: publisher tier, first-party pins, advisory route.** (1) Tier is recorded,
never scored, and waives nothing. "Actions created by GitHub are located in the `actions` and `github` organizations"
([settings docs](https://docs.github.com/en/enterprise-cloud@latest/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)). The verified creator badge means "GitHub has verified the creator of the action as a partner
organization", and listed Actions "aren't reviewed by GitHub" once they meet the listing requirements ([publishing docs](https://docs.github.com/en/enterprise-cloud@latest/actions/creating-actions/publishing-actions-in-github-marketplace?learn=create_actions&learnProduct=actions));
a [2022 partner post](https://partner.github.com/2022/11/07/why-should-action-partners-get-verified.html) names domain, email and a support contact. Every tier gets the full rubric, the hard stops and the
job test. (2) The pin rule covers first-party `actions/*` (closes the Day 1 open item). GitHub's "Require actions to be pinned to a
full-length commit SHA" setting "includes actions from your enterprise and actions authored by GitHub" (settings docs). checkout's
major tags move by design: "Workflows pinned to a floating major tag (e.g., `actions/checkout@v4`) will automatically pick up the
change" ([changelog](https://github.blog/changelog/2026-06-18-safer-pull_request_target-defaults-for-github-actions-checkout/), enforcement moved to 2026-07-20; v4.4.0 notes it as "[BREAKING]", [releases](https://github.com/actions/checkout/releases), first page,
no Immutable label seen). The cost: "Workflows pinned to a specific SHA, minor, or patch version aren't affected by the backport",
and Dependabot "will not create alerts for actions pinned to SHA values" ([GHES 3.11 page, discontinued](https://docs.github.com/en/enterprise-server@3.11/actions/security-guides/using-githubs-security-features-to-secure-your-use-of-github-actions)). So every pin
needs a named update route (Day 11). (3) Lockfiles are generally available since 2026-10-28 on Free, Team and Enterprise Cloud
([changelog](https://github.blog/changelog/2026-10-28-github-actions-workflow-lockfiles-are-generally-available/)): `.github/workflows/actions.lock` keeps tag references in the workflow and runs the locked commits, and a
Dependabot version update regenerates the entry. Transitive actions are included, "except" dependencies of reusable workflow calls;
the [concept page](https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles) says SHA pinning is then "no longer necessary" but still calls the feature public preview. A lockfile
does not yet satisfy this rule here: Chablis has not seen it run, and mismatch behaviour is unread. Day 11 compares, Day 14 sets
policy. (4) Advisory route for lessons: `gh api -X GET search/code -f q='"owner/name" repo:github/advisory-database'`
([database](https://github.com/github/advisory-database)), run beside known advisories searched the same way as positive controls, then read each hit's affected
package. On 2026-11-27 controls for four Actions surfaced; adding the JSON key `name` to the query returned 0 even for a known one.
No hit is a negative scoped to that search. The scout route stays queue #23.

## 7. Run contract — state back before any run of size

- **OBJECTIVE** — what data, for which project
- **SOURCE + ACCESS CLASS** — where it lives; PUBLIC / CREDENTIALED / LICENSED
- **AUTHORIZATION** — credential ref, license, or test scope if not PUBLIC
- **TARGET SCHEMA** — the shape it lands in, and the dedup key
- **FRESHNESS** — source class and TTL

## 8. Recon — secondary, authorized, passive first

Only on assets Blake owns or holds written scope to test. Record the
authorization (target, scope, date, grantor) before any active step.

- **Passive first** — certificate transparency, public DNS, WHOIS, public
  internet-scan data, technology fingerprinting. No packets to the target.
- **Active only within scope** — service enumeration, surface mapping,
  misconfiguration checks. A target not named in the authorization is out of scope.
- Findings go to the private Drive folder's `recon/`, each a scoped statement with method and time.

## 9. Cost

Token spend and Actions minutes are real costs; count both. The scout runs
without a model. The model runs on sonnet; opus only on named escalations.

## 10. The market data feed

*Decision 2026-11-18 (Blake): the feed is for Blake and his agents only — internal
research and thesis work, not redistributed.* Convenience sources that forbid
commercial use or redistribution (Yahoo via yfinance) and AGPL code (OpenBB)
are acceptable inside that boundary. If the feed is ever passed to others, re-test
every source and library against that use first.

**Three tiers, two lanes.**

| Tier | Sources | Lane | Runs |
|---|---|---|---|
| 1 | US-government: Treasury curve, FRED government series, CFTC COT, SEC EDGAR | public | GitHub Actions nightly → `chablis-feed` branch (public domain) |
| 2 | Crypto exchange public data via ccxt | private | On demand, Blake's Mac or another private runner |
| 3 | Licensed vendors (Massive, Databento, Alpaca…) behind Blake's keys | private | Same, only with a key |

**Rules.**
- The public lane carries only US-government data. A FRED series enters it only
  if its originator is a government body (Fed, Treasury, BLS, BEA); no
  index-vendor or exchange series.
- The private lane never writes inside the public repo; `feed.py` refuses.
- Point-in-time: SEC facts carry `as_of` = filing date, so a restated value is a
  new row, never an overwrite. Never backfill history with today's revised figure.
- A closed bar or a filed fact is `reference` class; a series subject to
  revision (macro) is `structural` and gets re-pulled.
- Every new source enters with a `Silent on:` scope, a license line and a
  rubric score for the library behind it (§6).

*Note 2026-11-19 (Day 1, LEARNING_LOG).* GitHub's scheduled runs lag their cron by
hours in this repo: all 12 scheduled `morning-brief-data` runs among the latest 30
fired 5.4–10.0 h late (cron 11:30Z, unchanged since added). A feed or scout cron set
an hour or two before the lesson cannot be ready for it. The lesson loads the newest
`feed/YYYY-MM-DD/` present, whatever its date. A reliable start is a push trigger
(`chablis-feed-trigger-*`, the pattern `morning-brief-data.yml` already uses) or a
cron at least 10 h earlier; either needs a workflow edit (handoff queue).

*Note 2026-11-21 (Day 3, LEARNING_LOG).* The Drive connector's `update_file` changes metadata
only, so the canonical `ledger.db` stays empty (queue #15). The lesson therefore loads each feed
into the newest dated ledger copy, which is cumulative, and saves the result as a new dated copy;
loading into the empty canonical would leave each dated copy holding one day. `load` is idempotent:
2026-11-21 read 9,986 rows and added 24.

*Note 2026-11-23 (Day 5, LEARNING_LOG).* The ledger outgrew the connector's per-call upload cap (3.5 MB against about
3.1 MB; 2026-11-22 saved nothing). A gzip of the vacuumed ledger is 329 KB, so the lesson now saves
`ledger-YYYY-MM-DD.db.gz` (`create_file`, `base64Content` as a file reference, `application/gzip`,
`disableConversionToGoogleType`) and loads from the newest `ledger-*.db.gz` or `ledger-*.db` by date. Round trip verified
2026-11-23: the downloaded file's SHA-256 equals the uploaded one, and gunzip yields a ledger with `integrity_check` ok and
13,803 rows. When a load is skipped or unsaved, the next lesson loads every missed feed directory, oldest first (today
loaded feeds 11-21 and 11-22 into the 11-21 copy: 1,913 new rows, all from 11-21). The canonical `ledger.db` stays empty (queue #15).

**Learning from GitHub.** Before writing an adapter, check whether a maintained
library already does it (edgartools, fredapi, ccxt, OpenBB providers), score it,
and use it if it clears the rubric; write stdlib code only where none does.
