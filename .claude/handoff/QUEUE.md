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
| 12 | 2026-11-19 | Chablis day 1 | gh | Pinning follow-ups. (a) SHA-pin the three tag-pinned `uses:` in `morning-brief-data.yml` to the pins already verified in `chablis-*.yml`: `actions/checkout@11d5960a326750d5838078e36cf38b85af677262` (v4.4.0) and `actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065` (v5.6.0), version in a comment; these equal what `@v4`/`@v5` resolve to today, so behavior is unchanged. (b) `chablis-keyed` (passes API-key secrets to a step, tag-pinned) lives only on branches `chablis-keyed-setup` and `chablis-keyed-trigger-001`; decide with the `chablis-data` branch results whether the probe is still wanted. Retire it (delete both branches) or SHA-pin it and move it to main. (c) After (a) and (b), decide whether to enable the repo's SHA-pinning enforcement (Settings > Actions > General; GitHub changelog 2025-08-15), once every workflow is pinned. | morning-brief run green on SHA pins; keyed probe retired or pinned; enforcement decision recorded |
| 13 | 2026-11-19 | Chablis day 1 | gh | Make the feed and scout available to the 4:53am lesson. Scheduled runs in this repo fire 5.4–10.0 h after cron (12 of 12 sampled), and `chablis-scout` / `chablis-feed` had 0 runs at 11:53Z on 2026-11-19. Add `push: branches: ["chablis-feed-trigger-*"]` and the scout equivalent, as `morning-brief-data.yml` does, with the trigger branch deleted after the run, so the lesson can start them; or move the crons at least 10 h earlier. Do this together with item 4. | Lesson finds same-morning `feed/` and `scout/` output |

## Done

| # | Done | By | Result |
|---|---|---|---|
