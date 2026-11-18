#!/usr/bin/env python3
"""Chablis market-data feed. Stdlib only; tier 2/3 adapters import their library only when used.

Commands
  run --lane public  --config F --out DIR   Tier 1: US-government sources (Treasury, FRED government
                                            series, CFTC, SEC). Public-domain data. Runs nightly on
                                            GitHub Actions and is committed to the chablis-feed branch.
  run --lane private --config F --out DIR   Tier 2/3: crypto (ccxt), Yahoo (yfinance), Massive. For
                                            Blake's own use only. Refuses to write inside the public repo.
  load --in DIR --ledger PATH [--project P] Load one run's output into the shared ledger, with lineage.
  selftest                                  Offline checks against fixtures.

Every record carries its source URL and retrieval time. Every source declares what it is silent on.
"""
import csv, io, json, os, sqlite3, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(HERE, "..", "ledger", "schema.sql")
UA = os.environ.get("CHABLIS_UA", "chablis-feed/0.1 (+https://github.com/jblakenunley/claude1)")
PUBLIC_REPO = "jblakenunley/claude1"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url, ua=UA, headers=None):
    """GET bytes. Returns (body, error). One polite retry on 429/503 honoring Retry-After."""
    h = {"User-Agent": ua, "Accept-Encoding": "identity", **(headers or {})}
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=60) as r:
                return r.read(), None
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt == 1:
                time.sleep(min(int(e.headers.get("Retry-After") or 5), 60))
                continue
            return None, f"HTTP {e.code}"
        except Exception as e:
            return None, f"{type(e).__name__}: {e}"
    return None, "retry exhausted"


def obs(series, d, value, unit, url, retrieved, label=None, as_of=None, extra=None):
    return {"kind": "observation", "series": series, "date": d, "value": value, "unit": unit,
            "as_of": as_of, "label": label, "extra": extra, "url": url, "retrieved_at": retrieved}


# ---------------------------------------------------------------- tier 1 parsers (pure, testable)

def parse_treasury_curve(text, url, retrieved, since):
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        m, d, y = row["Date"].split("/")
        iso = f"{y}-{m}-{d}"
        if iso < since:
            continue
        for col, v in row.items():
            if col == "Date" or not v:
                continue
            tenor = (col.replace(" Months", "M").replace(" Month", "M").replace(" Mo", "M")
                        .replace(" Yr", "Y").replace(" Wk", "W").replace(" ", ""))
            out.append(obs(f"UST_{tenor}", iso, float(v), "percent", url, retrieved, label=f"Treasury par yield {col}"))
    return out


def parse_fred_csv(text, series, url, retrieved):
    out = []
    r = csv.reader(io.StringIO(text))
    next(r, None)  # header: observation_date (or DATE), SERIES
    for row in r:
        if len(row) < 2 or row[1] in (".", ""):
            continue
        out.append(obs(f"FRED_{series}", row[0], float(row[1]), "as published", url, retrieved))
    return out


COT_FIELDS = ["open_interest_all", "noncomm_positions_long_all", "noncomm_positions_short_all",
              "comm_positions_long_all", "comm_positions_short_all"]


def parse_cftc(rows, url, retrieved):
    out = []
    for r in rows:
        code, d = r.get("cftc_contract_market_code"), (r.get("report_date_as_yyyy_mm_dd") or "")[:10]
        for f in COT_FIELDS:
            if r.get(f) not in (None, ""):
                out.append(obs(f"COT_{code}_{f}", d, float(r[f]), "contracts", url, retrieved,
                               label=r.get("market_and_exchange_names")))
    return out


def parse_sec_facts(facts, ticker, concepts, url, retrieved, since):
    """Point-in-time: one row per (period end, filing). as_of = the date it was filed."""
    out = []
    gaap = facts.get("facts", {}).get("us-gaap", {})
    for c in concepts:
        for unit, items in gaap.get(c, {}).get("units", {}).items():
            for it in items:
                if it.get("filed", "") < since:
                    continue
                out.append(obs(f"SEC_{ticker}_{c}", it["end"], it["val"], unit, url, retrieved, as_of=it.get("filed"),
                               extra={k: it.get(k) for k in ("fy", "fp", "form", "accn", "start")}))
    return out


def parse_sec_filings(sub, ticker, url, retrieved, since):
    rec = sub.get("filings", {}).get("recent", {})
    out = []
    for i, d in enumerate(rec.get("filingDate", [])):
        if d < since:
            continue
        out.append({"kind": "filing", "series": f"SEC_{ticker}_filing", "date": d, "value": None, "unit": None,
                    "as_of": d, "label": rec["form"][i], "url": url, "retrieved_at": retrieved,
                    "extra": {"accession": rec["accessionNumber"][i], "document": rec.get("primaryDocument", [None] * (i + 1))[i]}})
    return out


# ---------------------------------------------------------------- sources: (meta, fetcher)

def meta(sid, name, access, fclass, license_, scope):
    assert "Silent on:" in scope
    return {"source_id": sid, "name": name, "access_class": access, "freshness_class": fclass,
            "license": license_, "scope": scope}


def src_treasury(cfg, since):
    year = date.today().year
    url = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/"
           f"{year}/all?type=daily_treasury_yield_curve&field_tdr_date_value={year}")
    m = meta("SRC-UST-CURVE", "US Treasury daily par yield curve", "PUBLIC", "reference", "US Government work, public domain",
             "Daily par yield curve rates published by Treasury. Silent on: intraday moves, off-the-run issues, non-business days.")
    body, err = fetch(url)
    return m, [url], (parse_treasury_curve(body.decode(), url, now(), since) if body else []), err


def src_fred(cfg, since):
    m = meta("SRC-FRED-GOV", "FRED (government-source series only)", "PUBLIC", "structural",
             "Series from US government originators (Fed, Treasury, BLS, BEA); FRED terms apply",
             "Latest published values via FRED for the configured government series. "
             "Silent on: revision history (no vintages), any non-government series, values before the lookback.")
    rows, urls, errs = [], [], []
    for s in cfg.get("series", []):
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}&cosd={since}"
        urls.append(url)
        body, err = fetch(url)
        if err:
            errs.append(f"{s}: {err}")
        else:
            rows += parse_fred_csv(body.decode(), s, url, now())
        time.sleep(0.5)
    return m, urls, rows, "; ".join(errs) or None


def src_cftc(cfg, since):
    q = {"$where": f"report_date_as_yyyy_mm_dd >= '{since}T00:00:00'", "$limit": "50000"}
    if cfg.get("market_codes"):
        q["$where"] += " AND cftc_contract_market_code in (" + ",".join(f"'{c}'" for c in cfg["market_codes"]) + ")"
    url = "https://publicreporting.cftc.gov/resource/6dca-aqww.json?" + urllib.parse.urlencode(q)
    m = meta("SRC-CFTC-COT", "CFTC Commitments of Traders, legacy futures-only", "PUBLIC", "reference", "US Government work, public domain",
             "Weekly positions by trader class as of Tuesday. Silent on: options, intra-week changes, OTC swaps, individual traders.")
    body, err = fetch(url)
    return m, [url], (parse_cftc(json.loads(body), url, now()) if body else []), err


def src_sec(cfg, since):
    ua = os.environ.get("SEC_USER_AGENT")
    m = meta("SRC-SEC-EDGAR", "SEC EDGAR submissions and XBRL company facts", "PUBLIC", "reference", "US Government work, public domain",
             "Filings index and XBRL facts as filed, point-in-time by filing date. "
             "Silent on: private companies, intra-quarter figures, non-XBRL footnote detail, anything not yet filed.")
    if not ua:
        return m, [], [], "SEC_USER_AGENT not set (SEC requires a declared contact); skipped"
    rows, urls, errs = [], [], []
    for co in cfg.get("companies", []):
        cik, t = co["cik"].zfill(10), co["ticker"]
        for kind, url in (("sub", f"https://data.sec.gov/submissions/CIK{cik}.json"),
                          ("facts", f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")):
            urls.append(url)
            body, err = fetch(url, ua=ua)
            if err:
                errs.append(f"{t} {kind}: {err}")
            elif kind == "sub":
                rows += parse_sec_filings(json.loads(body), t, url, now(), since)
            else:
                rows += parse_sec_facts(json.loads(body), t, cfg.get("concepts", []), url, now(), since)
            time.sleep(0.2)  # SEC fair access: well under 10 requests/second
    return m, urls, rows, "; ".join(errs) or None


# ---------------------------------------------------------------- tier 2/3 (private lane)

def src_crypto(cfg, since):
    m = meta("SRC-CCXT-" + cfg.get("exchange", "kraken").upper(), f"{cfg.get('exchange', 'kraken')} public OHLCV via ccxt",
             "PUBLIC", "reference", "Exchange API terms; internal use",
             "Daily OHLCV from one exchange. Silent on: other venues, OTC, any consolidated price.")
    try:
        import ccxt
    except ImportError:
        return m, [], [], "ccxt not installed (pip install ccxt)"
    ex = getattr(ccxt, cfg.get("exchange", "kraken"))()
    rows, errs = [], []
    since_ms = int(datetime.fromisoformat(since).replace(tzinfo=timezone.utc).timestamp() * 1000)
    for sym in cfg.get("symbols", []):
        try:
            for t, o, h, l, c, v in ex.fetch_ohlcv(sym, "1d", since=since_ms):
                d = datetime.fromtimestamp(t / 1000, timezone.utc).strftime("%Y-%m-%d")
                rows.append(obs(f"CRYPTO_{ex.id}_{sym}_close", d, c, sym.split("/")[1], ex.urls.get("api", ex.id), now()))
                rows.append(obs(f"CRYPTO_{ex.id}_{sym}_volume", d, v, sym.split("/")[0], ex.urls.get("api", ex.id), now()))
        except Exception as e:
            errs.append(f"{sym}: {type(e).__name__}: {e}")
    return m, [ex.id], rows, "; ".join(errs) or None


def src_yahoo(cfg, since):
    m = meta("SRC-YAHOO", "Yahoo Finance via yfinance", "PUBLIC", "reference",
             "Yahoo API terms: personal, non-commercial use only; not for redistribution",
             "Daily bars from Yahoo's unofficial endpoints. Silent on: completeness guarantees, published rate limits; "
             "corporate-action adjustment is Yahoo's.")
    try:
        import yfinance as yf
    except ImportError:
        return m, [], [], "yfinance not installed (pip install yfinance)"
    rows, errs = [], []
    for t in cfg.get("tickers", []):
        try:
            h = yf.Ticker(t).history(start=since, auto_adjust=False)
            for idx, r in h.iterrows():
                d = idx.strftime("%Y-%m-%d")
                rows.append(obs(f"YF_{t}_close", d, float(r["Close"]), "USD", f"yfinance:{t}", now()))
                rows.append(obs(f"YF_{t}_volume", d, float(r["Volume"]), "shares", f"yfinance:{t}", now()))
        except Exception as e:
            errs.append(f"{t}: {type(e).__name__}: {e}")
        time.sleep(1)
    return m, [f"yfinance:{t}" for t in cfg.get("tickers", [])], rows, "; ".join(errs) or None


def src_massive(cfg, since):
    m = meta("SRC-MASSIVE", "Massive (formerly Polygon.io) daily aggregates", "CREDENTIALED", "reference",
             "Massive plan terms for the key in use",
             "Daily aggregates within the plan's entitlements. Silent on: data beyond the plan (the free plan is end-of-day, 2 years).")
    key = os.environ.get("MASSIVE_API_KEY")
    if not key:
        return m, [], [], "MASSIVE_API_KEY not set; skipped"
    m["auth_ref"] = "env MASSIVE_API_KEY (Blake's Massive account)"
    rows, urls, errs = [], [], []
    to = date.today().isoformat()
    for t in cfg.get("tickers", []):
        url = f"https://api.massive.com/v2/aggs/ticker/{t}/range/1/day/{since}/{to}?adjusted=false&limit=50000"
        urls.append(url)
        body, err = fetch(url, headers={"Authorization": f"Bearer {key}"})
        if err:
            errs.append(f"{t}: {err}")
            continue
        for b in json.loads(body).get("results", []) or []:
            d = datetime.fromtimestamp(b["t"] / 1000, timezone.utc).strftime("%Y-%m-%d")
            rows.append(obs(f"MSV_{t}_close", d, b["c"], "USD", url, now()))
            rows.append(obs(f"MSV_{t}_volume", d, b["v"], "shares", url, now()))
        time.sleep(13)  # free plan: 5 calls/minute
    return m, urls, rows, "; ".join(errs) or None


LANES = {
    "public": {"treasury_curve": src_treasury, "fred": src_fred, "cftc_cot": src_cftc, "sec": src_sec},
    "private": {"crypto": src_crypto, "yahoo": src_yahoo, "massive": src_massive},
}


def inside_public_repo(path):
    try:
        top = subprocess.run(["git", "-C", path, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        if top.returncode:
            return False
        origin = subprocess.run(["git", "-C", path, "remote", "get-url", "origin"], capture_output=True, text=True).stdout
        return PUBLIC_REPO in origin.lower()
    except FileNotFoundError:
        return False


def cmd_run(lane, config, out):
    with open(config, encoding="utf-8") as fh:
        cfg = json.load(fh)
    os.makedirs(out, exist_ok=True)
    if lane == "private" and inside_public_repo(out):
        print(f"refusing: {out} is inside the public repo; private-lane data never goes there")
        return 3
    since = (date.today() - timedelta(days=cfg.get("lookback_days", 30))).isoformat()
    manifest = {"generated_at": now(), "lane": lane, "since": since, "sources": []}
    for name, fn in LANES[lane].items():
        scfg = cfg.get(lane, {}).get(name)
        if not scfg or scfg.get("enabled") is False:
            continue
        m, urls, rows, err = fn(scfg, since)
        with open(os.path.join(out, f"{m['source_id']}.jsonl"), "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
        manifest["sources"].append({**m, "urls": urls, "count": len(rows), "error": err,
                                    "status": "failed" if err and not rows else "partial" if err else "complete"})
        print(f"{m['source_id']}: {len(rows)} rows{'  ERROR ' + err if err else ''}")
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    return 0


# ---------------------------------------------------------------- ledger load

def cmd_load(indir, ledger, project="chablis-feed"):
    with open(os.path.join(indir, "manifest.json"), encoding="utf-8") as fh:
        man = json.load(fh)
    db = sqlite3.connect(ledger)
    with open(SCHEMA, encoding="utf-8") as fh:
        db.executescript(fh.read())
    ttl = dict(db.execute("SELECT class, ttl_days FROM freshness_class"))
    loaded = 0
    for s in man["sources"]:
        db.execute("""INSERT INTO source(source_id,name,base_url,access_class,auth_ref,license,scope,freshness_class,load_mode)
                      VALUES(?,?,?,?,?,?,?,?,'upsert') ON CONFLICT(source_id) DO UPDATE SET scope=excluded.scope,
                      license=excluded.license, auth_ref=excluded.auth_ref""",
                   (s["source_id"], s["name"], (s["urls"] or [None])[0], s["access_class"], s.get("auth_ref"),
                    s["license"], s["scope"], s["freshness_class"]))
        pull_id = f"PULL-{man['generated_at'][:10]}-{s['source_id']}"
        db.execute("""INSERT OR REPLACE INTO pull(pull_id,source_id,project,started_at,finished_at,status,route,
                      authorization_ref,rows_in,missing) VALUES(?,?,?,?,?,?,?,?,?,?)""",
                   (pull_id, s["source_id"], project, man["generated_at"], man["generated_at"], s["status"],
                    f"chablis feed, {man['lane']} lane", s.get("auth_ref"), s["count"], s.get("error")))
        path = os.path.join(indir, f"{s['source_id']}.jsonl")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                valid = (datetime.fromisoformat(r["retrieved_at"].replace("Z", "+00:00")) +
                         timedelta(days=ttl[s["freshness_class"]])).strftime("%Y-%m-%dT%H:%M:%SZ")
                table = "market_filing" if r["kind"] == "filing" else "market_observation"
                db.execute(f"""INSERT OR REPLACE INTO {table}(series,date,as_of,value,unit,label,extra,
                               _source_id,_pull_id,_retrieved_at,_source_class,_valid_until,_current)
                               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,1)""",
                           (r["series"], r["date"], r.get("as_of") or "", r.get("value"), r.get("unit"), r.get("label"),
                            json.dumps(r.get("extra")) if r.get("extra") else None, s["source_id"], pull_id,
                            r["retrieved_at"], s["freshness_class"], valid))
                loaded += 1
    for t in ("market_observation", "market_filing"):
        db.execute(f"UPDATE {t} SET _current=0 WHERE _current=1 AND _valid_until < strftime('%Y-%m-%dT%H:%M:%SZ','now')")
    db.commit()
    print(f"loaded {loaded} rows from {len(man['sources'])} sources into {ledger}")
    return 0


# ---------------------------------------------------------------- selftest

def cmd_selftest():
    fx = lambda n: open(os.path.join(HERE, "fixtures", n), encoding="utf-8").read()
    t = parse_treasury_curve(fx("treasury.csv"), "u", "2026-11-18T00:00:00Z", "2026-11-01")
    assert {r["series"] for r in t} >= {"UST_1M", "UST_10Y", "UST_30Y"} and all(r["date"] >= "2026-11-01" for r in t), t[:3]
    f = parse_fred_csv(fx("fred.csv"), "DGS10", "u", "2026-11-18T00:00:00Z")
    assert len(f) == 2 and f[0]["series"] == "FRED_DGS10", f  # the "." row is skipped
    c = parse_cftc(json.loads(fx("cftc.json")), "u", "2026-11-18T00:00:00Z")
    assert len(c) == 5 and c[0]["date"] == "2026-11-10", c[:1]
    s = parse_sec_facts(json.loads(fx("sec_facts.json")), "NVDA", ["Revenues"], "u", "2026-11-18T00:00:00Z", "2025-01-01")
    assert len(s) == 1 and s[0]["as_of"] == "2025-11-19", s
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        man = {"generated_at": "2026-11-18T10:00:00Z", "lane": "public", "since": "2026-11-01", "sources": [
            {**meta("SRC-UST-CURVE", "t", "PUBLIC", "reference", "pd", "x Silent on: y"), "urls": ["u"], "count": len(t),
             "error": None, "status": "complete"}]}
        json.dump(man, open(os.path.join(d, "manifest.json"), "w"))
        with open(os.path.join(d, "SRC-UST-CURVE.jsonl"), "w") as fh:
            fh.writelines(json.dumps(r) + "\n" for r in t)
        db = os.path.join(d, "ledger.db")
        cmd_load(d, db)
        cmd_load(d, db)  # idempotent
        n = sqlite3.connect(db).execute("SELECT COUNT(*) FROM market_observation").fetchone()[0]
        assert n == len(t), (n, len(t))
    assert inside_public_repo(HERE) == (PUBLIC_REPO in subprocess.run(["git", "-C", HERE, "remote", "get-url", "origin"],
                                                                       capture_output=True, text=True).stdout.lower())
    print(f"selftest ok (treasury {len(t)}, fred {len(f)}, cftc {len(c)}, sec {len(s)}; load idempotent)")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    arg = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    if a[:1] == ["run"] and arg("--lane") in LANES and arg("--config") and arg("--out"):
        sys.exit(cmd_run(arg("--lane"), arg("--config"), arg("--out")))
    if a[:1] == ["load"] and arg("--in") and arg("--ledger"):
        sys.exit(cmd_load(arg("--in"), arg("--ledger"), arg("--project", "chablis-feed")))
    if a[:1] == ["selftest"]:
        sys.exit(cmd_selftest())
    print(__doc__)
    sys.exit(2)
