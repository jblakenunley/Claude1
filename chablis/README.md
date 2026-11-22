# Chablis

Data-acquisition agent for the 1+Claude system, and the house expert on GitHub
tool quality and selection. "Chablis exists to connect you to data."

| File | Purpose |
|---|---|
| `../.claude/agents/chablis.md` | Agent definition (Claude Code subagent) |
| `DOCTRINE.md` | The overarching instructions and the tool rubric (§6) |
| `LEARNING_PATH.md` | 30-day curriculum on GitHub tool quality and selection |
| `LEARNING_LOG.md` | Dated findings, one per lesson |
| `TOOL_REGISTRY.md` | Every tool vetted: scores, evidence, review dates |
| `watchlist.json` | Repos the nightly scout pulls signals for |
| `scout.py` | Signal collector and Actions pin audit (stdlib, no model) |
| `upkeep.py` | Upkeep bands from treeless git clones; `scout` mode adds an `upkeep` block to the nightly scout JSON |
| `ledger/schema.sql` | Shared ledger schema, including the market data tables |
| `feed/feed.py` | Market data feed: public lane (US-government sources), private lane (crypto, Yahoo, Massive), ledger loader |
| `feed/feed_config.json` | Which series, contracts and companies the feed pulls |
| `progress.json` | Where the path stands |

## Use

In Claude Code from this repo:

- `Have chablis source <dataset> for <project>` — states the run contract, then pulls
- `Ask chablis to vet <owner/repo>` — scores it against the rubric and records it
- `Have chablis run today's lesson` — advances the path one day and commits

## How it runs on its own

1. **Scout** — `.github/workflows/chablis-scout.yml` runs nightly on GitHub,
   pulls tool signals (GitHub API, OpenSSF Scorecard) and commits them to the
   `chablis-scout` branch.
   No model, no token cost.
2. **Feed** — `.github/workflows/chablis-feed.yml` runs nightly on GitHub, pulls
   the public lane and commits it to the `chablis-feed` branch.
3. **Lesson** — a scheduled task runs the daily lesson on sonnet: reads the
   scout output, loads last night's feed into the private ledger, scores tools,
   updates the registry and log, commits here.

## Public vs private

This repo is public: code, doctrine, registry, and scout output (public
metadata about public repos) on the `chablis-scout` branch. Pulled data, the
shared ledger and recon findings live only in the private Google Drive folder
"Chablis Data (private)": `ledger.db`, `pulls/`, `recon/`.
