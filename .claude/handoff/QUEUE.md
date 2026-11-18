# Claude Code handoff queue

Work that cloud sessions cannot do — it needs Blake's Mac, a browser signed in as him,
GitHub settings or secrets, local files, or an unrestricted network. Cloud sessions
append here; Claude Code on the Mac works it with `/handoff`.

**This repo is public.** Items describe the task, never the private detail. A secret,
a personal record or a private name goes in the private Drive folder
"Chablis Data (private)" and the item points there.

**Blake is not the operator.** Claude Code does each item itself. The only things
that come to Blake are the ones that are genuinely his: a sign-in, an approval, or
a choice only he can make. Those are gathered and asked once, together, at the
start of a `/handoff` run.

Needs: `gh` = GitHub CLI signed in as Blake · `browser` = Chrome with Claude in Chrome ·
`secret` = a key or credential · `local` = files or network on the Mac · `choice` = Blake decides

## Open

| # | Added | From | Needs | Task | Done when |
|---|---|---|---|---|---|
| 1 | 2026-11-18 | White Hat Hacker / Chablis | gh | **Prerequisite.** Sign the GitHub CLI in as Blake on the Mac (`gh auth login --web`; Blake approves the browser prompt). Confirm `gh auth status` shows the `workflow` scope. | `gh auth status` clean, workflow scope present |
| 2 | 2026-11-18 | White Hat Hacker / Chablis | browser | **Prerequisite.** Get Claude in Chrome connecting to Claude sessions: check the extension is installed, signed in to the same account, enabled, and visible to the session (`list_connected_browsers`). Record what was wrong. | A session lists the Mac's Chrome as connected |
| 3 | 2026-11-18 | White Hat Hacker / Chablis | gh, choice | Set repo variable `SEC_USER_AGENT` on jblakenunley/claude1 (`gh variable set`). SEC requires a declared contact; Blake chooses which address. Repo variables are not shown publicly. | Variable set; next feed run's SEC source not skipped |
| 4 | 2026-11-18 | White Hat Hacker / Chablis | gh | Trigger the first runs instead of waiting for the schedule: `gh workflow run chablis-scout.yml` and `gh workflow run chablis-feed.yml`; read the logs on the `chablis-scout` and `chablis-feed` branches; fix any source that fails. | Both runs green; manifest statuses complete or explained |
| 5 | 2026-11-18 | White Hat Hacker / Chablis | secret, local | Store Blake's Massive API key in the macOS keychain (Blake supplies it; never written to a file or the repo). | Key retrievable by `security find-generic-password` |
| 6 | 2026-11-18 | White Hat Hacker / Chablis | local | Automate the feed's private lane on the Mac: a launchd job that runs `chablis/feed/feed.py run --lane private` nightly into a folder outside the repo (key from the keychain), loads it into a local ledger, and syncs the ledger to the Drive folder. `pip install ccxt yfinance` in a venv. | launchd job runs; private rows in the ledger |
| 7 | 2026-11-18 | Commercial register | local | Move the register's code repo (`nunley-register/` rev. 7, local disk only) into private storage — a private GitHub repo or the private Drive folder — so automation can reach it. | Repo reachable from a cloud session |
| 8 | 2026-11-18 | White Hat Hacker / Chablis | gh, choice | Optional: create private repo `jblakenunley/claude1-data` and move the ledger and private files from Drive to it, if Blake wants git history over Drive. | Blake says yes and the move is done, or says no |
| 9 | 2026-11-18 | Snowflake | gh, secret | On or after 2026-12-18 (30-day review): if Blake approves moving Snowflake's daily lesson onto GitHub Actions, set `ANTHROPIC_API_KEY` as a repo secret and build the workflow. | Blake's decision recorded; workflow live or item closed |
| 10 | 2026-11-18 | Several (Dragonwing, register, morning brief) | browser | Authenticated and blocked sources — LinkedIn first (named a critical blocker), then county/state portals and paywalled local press — through Chrome signed in as Blake. Build one reusable Claude in Chrome routine per source; record which sources work. | Routine per source recorded; LinkedIn working |
| 11 | 2026-11-18 | Commercial register | local | Check the status of the document archive restore that has blocked the register since Aug 2026. If it is available on the Mac, run the single structured intake pass against the target list (private details in the register's Drive BOOT file). Claude Code does the reading; nothing is handed to Blake to find. | Restore status recorded; intake pass done if available |

## Done

| # | Done | By | Result |
|---|---|---|---|
