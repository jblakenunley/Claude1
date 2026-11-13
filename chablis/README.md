# Chablis source prober

Finds out which public market-data sources actually answer, at scale, and records what each returned.

- `chablis_probe.py` reads each host's robots.txt first (a refusal is final and is recorded, never worked around),
  makes one request per URL and at most one per second per host, and writes status, format, size and newest date.
- `seeds.json` holds known endpoints with a concrete test URL. `candidates.json` holds the harvested
  public-apis entries (finance, crypto, currency, government, open data).
- The workflow `.github/workflows/chablis-probe.yml` runs it on GitHub's servers and commits the results to the
  `chablis-data` branch (`probe/DATE.json` and `probe/latest.json`). Push any branch named `chablis-trigger-*`, or use
  Run workflow, to start a run.
