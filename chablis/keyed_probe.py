"""Keyed Chablis probes. Keys come from environment variables (repo secrets); never printed."""
import os, json, time, datetime, requests
UA = {"User-Agent": "Chablis/1.0 (public-source research)"}
out = {"run": datetime.datetime.utcnow().isoformat() + "Z"}
def key(n): return os.environ.get(n, "")

k = key("OPENFIGI_API_KEY")
tick = ["NVDA", "ORCL", "CRWV", "NBIS", "SMCI", "DELL", "AMD", "AVGO"]
if k:
    r = requests.post("https://api.openfigi.com/v3/mapping",
        headers={**UA, "Content-Type": "application/json", "X-OPENFIGI-APIKEY": k},
        json=[{"idType": "TICKER", "idValue": t, "exchCode": "US"} for t in tick], timeout=30)
    out["openfigi"] = {"status": r.status_code,
        "rows": [(d.get("data") or [{}])[0].get("figi") for d in r.json()] if r.ok else r.text[:200]}
else: out["openfigi"] = "no key"

k = key("CENSUS_API_KEY")
if k:
    r = requests.get("https://api.census.gov/data/2023/acs/acs1", params={"get": "NAME,B01001_001E", "for": "state:06", "key": k}, headers=UA, timeout=30)
    out["census"] = {"status": r.status_code, "body": r.text[:200]}
else: out["census"] = "no key"

k = key("ALPHAVANTAGE_API_KEY")
if k:
    res = {}
    for fn in ["GLOBAL_QUOTE", "EARNINGS", "OVERVIEW"]:
        r = requests.get("https://www.alphavantage.co/query", params={"function": fn, "symbol": "NVDA", "apikey": k}, headers=UA, timeout=30)
        t = r.text
        res[fn] = "premium" if "premium" in t.lower() else ("rate-limited" if "spreading out" in t else "ok")
        time.sleep(2)
    out["alphavantage"] = res
else: out["alphavantage"] = "no key"
print(json.dumps(out, indent=1))
