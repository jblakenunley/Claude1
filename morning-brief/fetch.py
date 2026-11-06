#!/usr/bin/env python3
"""Morning Brief data fetcher.

Pulls snow, forecast, avalanche, road, resort and market data from machine-readable
public feeds and writes one JSON file of clean numbers in US units. The paper reads only
the "paper" fields; everything under "archive" (fetch log, forecast calls, scores) is for
the archive record and is never printed.

    python3 fetch.py run --date 2026-11-06 --out data/2026-11-06.json --history data
    python3 fetch.py validate data/2026-11-06.json
    python3 fetch.py selftest

Needs plain internet access (GitHub Actions, a laptop). The CDOT key comes from the
CDOT_API_KEY environment variable and is never written to the output.
Python 3.9+, standard library only.
"""
import argparse, csv, io, json, os, re, statistics, sys, time, urllib.parse, urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
MT = ZoneInfo("America/Denver")
ET = ZoneInfo("America/New_York")
LOG = []  # fetch log, goes to archive only


# ---------------------------------------------------------------- HTTP
def get(url, ua, accept="*/*", label=None, timeout=25):
    """GET with one retry. Returns text or None; records the outcome in LOG without the key."""
    safe = re.sub(r"apiKey=[^&]+", "apiKey=***", url)
    for attempt in (1, 2):
        t0 = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": accept})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read().decode("utf-8", "replace")
            LOG.append({"source": label or safe, "url": safe, "status": "ok", "ms": int((time.time() - t0) * 1000)})
            return body
        except Exception as e:  # noqa: BLE001 - every failure is logged and the slot is omitted
            err = f"{type(e).__name__}: {e}"[:160]
            if attempt == 2:
                LOG.append({"source": label or safe, "url": safe, "status": "failed", "error": err})
            else:
                time.sleep(2)
    return None


def get_json(url, ua, label=None, accept="application/json"):
    body = get(url, ua, accept=accept, label=label)
    if body is None:
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        LOG.append({"source": label or url, "status": "bad_json"})
        return None


# ---------------------------------------------------------------- units
def c_to_f(c):
    return None if c is None else round(c * 1.8 + 32)


def mm_to_in(mm):
    return None if mm is None else round(mm / 25.4, 1)


def num(s):
    try:
        v = float(str(s).strip())
        return v
    except (TypeError, ValueError):
        return None


def r1(v):
    return None if v is None else round(v, 1)


# ---------------------------------------------------------------- SNOTEL (NRCS report generator CSV)
SNOTEL_BASE = "https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/customMultipleStationReport/daily/"


def snotel_url(ids, start="-1", end="0"):
    trip = "%7C".join(f"{i}:CO:SNTL" for i in ids)
    return f"{SNOTEL_BASE}{trip}/{start},{end}/stationId,name,WTEQ::value,SNWD::value,WTEQ::pctOfMedian_1991"


def parse_snotel_csv(text):
    """Return {station_id: {date_iso: {name, swe_in, depth_in, pct_median}}}. NRCS reports inches."""
    lines = [l for l in text.splitlines() if l.strip() and not l.startswith("#")]
    if not lines:
        return {}
    rows = list(csv.reader(lines))
    head = [h.lower() for h in rows[0]]

    def col(*keys):
        for i, h in enumerate(head):
            if all(k in h for k in keys):
                return i
        return None

    c_date, c_id, c_name = col("date"), col("station id"), col("station name")
    c_swe = col("snow water equivalent", "start of day") or col("snow water equivalent (in)")
    c_dep = col("snow depth")
    c_pct = col("% of median")
    if c_swe is not None and c_swe == c_pct:  # guard against the % column matching the SWE key
        c_swe = None
    if "(cm)" in " ".join(head) or "(mm)" in " ".join(head):
        raise ValueError("SNOTEL returned metric columns; request English units")
    out = {}
    for r in rows[1:]:
        if c_date is None or len(r) <= c_date:
            continue
        sid = r[c_id].strip() if c_id is not None else (r[c_name].strip() if c_name is not None else "?")
        d = r[c_date].strip()[:10]
        rec = {"name": r[c_name].strip() if c_name is not None else sid,
               "swe_in": num(r[c_swe]) if c_swe is not None else None,
               "depth_in": num(r[c_dep]) if c_dep is not None else None,
               "pct_median": num(r[c_pct]) if c_pct is not None else None}
        out.setdefault(sid, {})[d] = rec
    return out


def snotel_block(raw, ids, day, names=None):
    """Clean per-station rows for `day` with 24h change; drops a station whose name doesn't match config."""
    stations, dropped = [], []
    y = (date.fromisoformat(day) - timedelta(days=1)).isoformat()
    for sid in ids:
        series = raw.get(str(sid), {})
        today, yday = series.get(day), series.get(y)
        if not today:
            continue
        want = (names or {}).get(str(sid))
        if want and want.split()[0].lower().replace(" ", "") not in today["name"].lower().replace(" ", ""):
            dropped.append({"id": sid, "expected": want, "got": today["name"]})
            continue
        s = {"id": sid, "name": want or today["name"], "swe_in": r1(today["swe_in"]), "depth_in": today["depth_in"],
             "pct_median": round(today["pct_median"]) if today["pct_median"] is not None else None}
        if yday:
            if today["swe_in"] is not None and yday["swe_in"] is not None:
                s["swe_24h_in"] = r1(today["swe_in"] - yday["swe_in"])
            if today["depth_in"] is not None and yday["depth_in"] is not None:
                s["depth_24h_in"] = today["depth_in"] - yday["depth_in"]
        stations.append(s)
    return stations, dropped


def median_of(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return round(statistics.median(vals), 1) if vals else None


# ---------------------------------------------------------------- NWS (api.weather.gov)
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "eighteen": 18, "twenty": 20}


def _n(tok):
    tok = tok.lower()
    return float(tok) if re.fullmatch(r"\d+(\.\d+)?", tok) else WORDS.get(tok)


def snow_band(text):
    """NWS public wording -> (label, low_in, high_in). None when the period carries no snow wording."""
    t = (text or "").lower()
    if "snow accumulation" not in t and "inches possible" not in t and "inch possible" not in t:
        return None
    if re.search(r"little or no (new )?snow accumulation", t):
        return ("0 in", 0.0, 0.0)
    m = re.search(r"less than (half an|one|a half) inch", t)
    if m:
        return ("under ½ in", 0.0, 0.5) if "half" in m.group(1) else ("under 1 in", 0.0, 1.0)
    m = re.search(r"(?:of |accumulation of )?(\w+) to (\w+) inch", t)
    if m and _n(m.group(1)) is not None and _n(m.group(2)) is not None:
        lo, hi = _n(m.group(1)), _n(m.group(2))
        return (f"{lo:g}–{hi:g} in", lo, hi)
    m = re.search(r"around (\w+) inch", t)
    if m and _n(m.group(1)) is not None:
        v = _n(m.group(1))
        return (f"about {v:g} in", v, v)
    return None


def nws_forecast(lat, lon, ua):
    pts = get_json(f"https://api.weather.gov/points/{lat},{lon}", ua, "NWS points", "application/geo+json")
    if not pts:
        return None
    url = pts.get("properties", {}).get("forecast")
    fc = get_json(url, ua, "NWS forecast", "application/geo+json") if url else None
    if not fc:
        return None
    p = fc.get("properties", {})
    periods = []
    for x in p.get("periods", []):
        temp = x.get("temperature")
        if x.get("temperatureUnit") == "C":
            temp = c_to_f(temp)
        st = datetime.fromisoformat(x["startTime"]).astimezone(MT)
        en = datetime.fromisoformat(x["endTime"]).astimezone(MT)
        band = snow_band(x.get("detailedForecast"))
        periods.append({"name": x.get("name"), "start": st.isoformat(), "end": en.isoformat(), "day": x.get("isDaytime"),
                        "temp_f": temp, "pop_pct": (x.get("probabilityOfPrecipitation") or {}).get("value"),
                        "short": x.get("shortForecast"), "band": band})
    return {"issued": p.get("updateTime") or p.get("generatedAt"), "periods": periods,
            "zone": pts.get("properties", {}).get("forecastZone", "").rsplit("/", 1)[-1]}


def summit_days(fc, n=5):
    days, order = {}, []
    for p in fc["periods"]:
        d = p["start"][:10]
        if d not in days:
            days[d] = {"date": d, "day": datetime.fromisoformat(p["start"]).strftime("%a")}
            order.append(d)
        rec = days[d]
        if p["day"]:
            rec["high_f"] = p["temp_f"]
            if p["band"]:
                rec["snow_day"] = p["band"][0]
        else:
            rec["low_f"] = p["temp_f"]
            if p["band"]:
                rec["snow_night"] = p["band"][0]
        if p["pop_pct"] is not None:
            rec["pop_pct"] = max(rec.get("pop_pct", 0), p["pop_pct"])
    return [days[d] for d in order][:n]


def next48(fc):
    """The biggest single NWS band in the next four periods, with its period name. Never a sum."""
    best = None
    for p in fc["periods"][:4]:
        if p["band"] and (best is None or p["band"][2] > best[1][2]):
            best = (p["name"], p["band"])
    if best is None:
        return {"text": "none", "low_in": 0.0, "high_in": 0.0, "when": None}
    return {"text": best[1][0], "low_in": best[1][1], "high_in": best[1][2], "when": best[0]}


def nws_alerts(lat, lon, ua):
    js = get_json(f"https://api.weather.gov/alerts/active?point={lat},{lon}", ua, "NWS alerts", "application/geo+json")
    out = []
    for f in (js or {}).get("features", []):
        pr = f.get("properties", {})
        ends = pr.get("ends") or pr.get("expires")
        until = datetime.fromisoformat(ends).astimezone(MT).strftime("%a %-I%p").lower().capitalize() if ends else None
        out.append({"event": pr.get("event"), "until": until})
    return out


# ---------------------------------------------------------------- avalanche (avalanche.org public API)
DANGER = {1: "Low", 2: "Moderate", 3: "Considerable", 4: "High", 5: "Extreme"}


def _inside(lon, lat, ring):
    hit = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if (y1 > lat) != (y2 > lat) and lon < (x2 - x1) * (lat - y1) / (y2 - y1) + x1:
            hit = not hit
    return hit


def caic(ua):
    """CAIC forecast zones as [(polygons, danger)]. avalanche.org names every CAIC zone alike, so zones are
    matched by location, not name."""
    js = get_json("https://api.avalanche.org/v2/public/products/map-layer/CAIC", ua, "CAIC via avalanche.org")
    zones = []
    for f in (js or {}).get("features", []):
        g = f.get("geometry") or {}
        polys = [g["coordinates"]] if g.get("type") == "Polygon" else g.get("coordinates", []) if g.get("type") == "MultiPolygon" else []
        lvl = (f.get("properties") or {}).get("danger_level")
        zones.append(([[[tuple(pt[:2]) for pt in ring] for ring in poly] for poly in polys], DANGER.get(lvl, "No rating")))
    return zones


def caic_at(zones, lat, lon):
    for polys, lvl in zones:
        for poly in polys:
            if poly and _inside(lon, lat, poly[0]) and not any(_inside(lon, lat, hole) for hole in poly[1:]):
                return lvl
    return None


# ---------------------------------------------------------------- resorts (Liftie open API)
def resort_status(name, cfg, today, ua):
    r = cfg["resorts"].get(name, {})
    out = {"name": name}
    js = get_json(f"https://liftie.info/api/resort/{r['liftie']}", ua, f"Liftie {name}") if r.get("liftie") and cfg.get("use_liftie") else None
    stats = ((js or {}).get("lifts") or {}).get("stats") or {}
    running = (stats.get("open") or 0) + (stats.get("hold") or 0)
    total = sum(v for k, v in stats.items() if isinstance(v, int))
    if js and running:
        out.update(status="Open", lifts_open=running, lifts_total=total)
    elif r.get("opens") and r["opens"] == today:
        out.update(status="Opens today")
    elif r.get("opens") and r["opens"] > today:
        d = date.fromisoformat(r["opens"])
        out.update(status=f"Opens {d.day} {d.strftime('%b')}")
    elif js:
        out.update(status="Closed")
    return out


# ---------------------------------------------------------------- roads (COtrip official feeds)
NOGO = re.compile(r"(road|highway|pass|safety|full|seasonal|canyon) closure|closed (in )?both directions|"
                  r"all lanes closed|road closed|highway closed|pass closed|is closed|chain law", re.I)
CAUTION = re.compile(r"lane clos|shoulder clos|traction law|icy|black ice|snow ?packed|slush|snow|"
                     r"delays?|construction|crash|rock ?fall|flood|wet", re.I)


def _route_key(s):
    s = re.sub(r"[^A-Z0-9]", "", str(s).upper())
    s = s.replace("INTERSTATE", "I").replace("SH", "CO").replace("STATEHIGHWAY", "CO")
    return re.sub(r"^(I|US|CO)0*", r"\1", s)


def _flat(o, acc=None):
    acc = [] if acc is None else acc
    if isinstance(o, dict):
        for v in o.values():
            _flat(v, acc)
    elif isinstance(o, list):
        for v in o:
            _flat(v, acc)
    elif isinstance(o, str):
        acc.append(o)
    return acc


def _mileposts(pr, text):
    mps = []
    for k, v in pr.items():
        if re.search(r"(marker|milepost|mile_?point|mm)$", k, re.I) and num(v) is not None:
            mps.append(num(v))
    if not mps:
        mps = [float(x) for x in re.findall(r"\b(?:MP|mile ?(?:post|marker|point))\s*(\d+(?:\.\d+)?)", text, re.I)]
    return mps


def _active(pr, now):
    st = pr.get("startTime") or pr.get("start_date")
    en = pr.get("endTime") or pr.get("clearTime") or pr.get("end_date")
    try:
        if st and datetime.fromisoformat(st.replace("Z", "+00:00")) > now:
            return False
        if en and datetime.fromisoformat(en.replace("Z", "+00:00")) < now:
            return False
    except ValueError:
        pass
    return True


def road_features(key, ua):
    feats = []
    for feed in ("incidents", "plannedEvents", "roadConditions"):
        js = get_json(f"https://data.cotrip.org/api/v1/{feed}?apiKey={key}", ua, f"COtrip {feed}")
        if js is None:
            continue
        for f in js.get("features", []):
            pr = f.get("properties", {})
            text = " ".join(_flat(pr))
            route = pr.get("routeName") or pr.get("route") or pr.get("roadName") or ""
            feats.append({"feed": feed, "route": _route_key(route), "text": text, "mps": _mileposts(pr, text), "props": pr})
    return feats


def road_verdicts(routes, feats, now):
    if not feats:
        return []
    out = []
    for rt in routes:
        hits = []
        for rk, lo, hi in rt["segments"]:
            for f in feats:
                if f["route"] != _route_key(rk) or not _active(f["props"], now):
                    continue
                if f["mps"] and not any(lo <= m <= hi for m in f["mps"]):
                    continue
                hits.append(f)
        verdict, reason = "GO", "No closures or incidents reported"
        for f in hits:
            if NOGO.search(f["text"]):
                verdict = "NO-GO"
                mp = sorted(f["mps"])
                reason = f"Closed MP {mp[0]:g} to {mp[-1]:g}" if len(mp) >= 2 else "Closed"
                if re.search(r"chain law", f["text"], re.I) and not re.search(r"clos", f["text"], re.I):
                    reason = "Chain law in effect"
                break
        if verdict == "GO":
            for f in hits:
                m = CAUTION.search(f["text"])
                if m:
                    verdict, reason = "CAUTION", m.group(0).strip().capitalize()
                    break
        out.append({"route": rt["name"], "verdict": verdict, "reason": reason, "matched": len(hits)})
    return out


# ---------------------------------------------------------------- markets (Yahoo chart API, FRED fallback)
def market(m, ua):
    """Last price, its trading day in the exchange's own time zone, and the change from the prior day's close."""
    js = get_json(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(m['yahoo'])}?range=5d&interval=1d",
                  ua, f"Yahoo {m['name']}")
    try:
        res = js["chart"]["result"][0]
        meta = res["meta"]
        tz = ZoneInfo(meta.get("exchangeTimezoneName") or "America/New_York")
        last, t_last = meta["regularMarketPrice"], meta["regularMarketTime"]
        last_day = datetime.fromtimestamp(t_last, tz).date()
        closes = [(datetime.fromtimestamp(t, tz).date(), c)
                  for t, c in zip(res["timestamp"], res["indicators"]["quote"][0]["close"]) if c is not None]
        prev = next(c for d, c in reversed(closes) if d < last_day)
    except (TypeError, KeyError, IndexError, ValueError, StopIteration):
        if m.get("fred"):
            txt = get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={m['fred']}", ua, label=f"FRED {m['fred']}")
            rows = [r for r in csv.reader(io.StringIO(txt or "")) if len(r) == 2 and num(r[1]) is not None]
            if len(rows) >= 2:
                last, prev = num(rows[-1][1]), num(rows[-2][1])
                return {"name": m["name"], "value": round(last, 3), "change_bp": round((last - prev) * 100),
                        "as_of": rows[-1][0], "fmt": m["fmt"]}
        return None
    if m["fmt"] == "yield" and last > 20:  # older ^TNX quotes were yield x10
        last, prev = last / 10, prev / 10
    out = {"name": m["name"], "value": round(last, {"yield": 3, "fx": 4}.get(m["fmt"], 2)), "as_of": last_day.isoformat(), "fmt": m["fmt"]}
    if m["fmt"] == "yield":
        out["change_bp"] = round((last - prev) * 100)
    else:
        out["change_pct"] = round((last / prev - 1) * 100, 1)
    return out


# ---------------------------------------------------------------- forecast scorebook (archive only)
def record_calls(fc, today, source):
    calls = []
    for d in summit_days(fc, n=3):
        bands = [p["band"] for p in fc["periods"] if p["start"][:10] == d["date"] and p["band"]]
        if not bands:
            continue
        calls.append({"source": source, "issued": fc["issued"], "date": d["date"],
                      "low_in": sum(b[1] for b in bands), "high_in": sum(b[2] for b in bands),
                      "bands": [b[0] for b in bands], "lead_days": (date.fromisoformat(d["date"]) - date.fromisoformat(today)).days})
    return calls


def score_calls(history, today):
    """Score calls whose day has passed: observed = median of the 7 Aspen stations' depth gain from
    start of that day to start of the next (SNOTEL daily is start-of-day). Returns new scores."""
    depth = {}  # date -> {id: depth}
    for rec in history:
        for s in rec.get("paper", {}).get("snow", {}).get("stations", []):
            depth.setdefault(rec["date"], {})[s["id"]] = s.get("depth_in")
    done = {(s["source"], s["issued"], s["date"]) for rec in history for s in rec.get("archive", {}).get("scores", [])}
    scores = []
    for rec in history:
        for c in rec.get("archive", {}).get("forecast_calls", []):
            nxt = (date.fromisoformat(c["date"]) + timedelta(days=1)).isoformat()
            if nxt > today or (c["source"], c["issued"], c["date"]) in done:
                continue
            a, b = depth.get(c["date"], {}), depth.get(nxt, {})
            gains = [max(0, b[i] - a[i]) for i in a if i in b and a[i] is not None and b[i] is not None]
            if len(gains) < 4:
                continue
            obs = statistics.median(gains)
            verdict = "hit" if c["low_in"] <= obs <= c["high_in"] else ("high" if obs < c["low_in"] else "low")
            scores.append({**{k: c[k] for k in ("source", "issued", "date", "low_in", "high_in")}, "observed_in": obs,
                           "verdict": verdict, "error_in": round((c["low_in"] + c["high_in"]) / 2 - obs, 1),
                           "stations": len(gains)})
            done.add((c["source"], c["issued"], c["date"]))
    return scores


# ---------------------------------------------------------------- news candidates (free RSS/Atom feeds)
import html as _html
import xml.etree.ElementTree as XET
from email.utils import parsedate_to_datetime


def _clean(t, n=320):
    t = re.sub(r"<[^>]+>", " ", _html.unescape(t or ""))
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"


def _when(s):
    if not s:
        return None
    try:
        d = parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(s.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def parse_feed(text):
    """RSS 2.0 or Atom -> [{title, url, published (aware datetime), summary}]."""
    root = XET.fromstring(text.encode("utf-8") if isinstance(text, str) else text)
    out = []
    for it in root.iter():
        tag = it.tag.rsplit("}", 1)[-1]
        if tag not in ("item", "entry"):
            continue
        f = {c.tag.rsplit("}", 1)[-1]: c for c in it}
        link = f.get("link")
        url = (link.get("href") or link.text) if link is not None else None
        pub = next((f[k].text for k in ("pubDate", "published", "updated", "date") if k in f and f[k].text), None)
        summ = next((f[k].text for k in ("description", "summary", "content") if k in f and f[k].text), "")
        title = f["title"].text if "title" in f else None
        if title and url:
            out.append({"title": _clean(title, 200), "url": url.strip(), "published": _when(pub), "summary": _clean(summ)})
    return out


def collect_news(cfg, day, ua, now=None):
    """Headlines from free feeds inside the window: 24h, 72h on Mondays, or a feed's own window_days."""
    now = now or datetime.now(timezone.utc)
    base_h = 72 if date.fromisoformat(day).weekday() == 0 else 26
    seen, items = set(), []
    for f in cfg.get("news_feeds", []):
        txt = get(f["url"], ua, accept="application/rss+xml, application/atom+xml, */*", label=f"RSS {f['outlet']}")
        if not txt:
            continue
        try:
            entries = parse_feed(txt)
        except (XET.ParseError, ValueError):
            LOG.append({"source": f"RSS {f['outlet']}", "status": "bad_xml"})
            continue
        hours = f.get("window_days", 0) * 24 or base_h
        kept = 0
        for e in entries:
            if not e["published"] or (now - e["published"]).total_seconds() > hours * 3600 or e["published"] > now:
                continue
            key = re.sub(r"\W+", "", e["title"].lower())[:80]
            if e["url"] in seen or key in seen:
                continue
            seen.update({e["url"], key})
            items.append({"outlet": f["outlet"], "hint": f["section"], "title": e["title"], "url": e["url"],
                          "published": e["published"].astimezone(MT).isoformat(timespec="minutes"), "summary": e["summary"]})
            kept += 1
            if kept >= 12:
                break
    items.sort(key=lambda x: x["published"], reverse=True)
    return items


# ---------------------------------------------------------------- assemble
def fmt_time(iso):
    if not iso:
        return None
    t = datetime.fromisoformat(str(iso).replace("Z", "+00:00")).astimezone(MT)
    return f"{t.day} {t.strftime('%b')} {t.strftime('%-I:%M%p').lower()}"


def safely(archive, name, fn, default=None):
    """One source failing must never stop the others: log it and leave the slot empty."""
    try:
        return fn()
    except Exception as e:  # noqa: BLE001
        archive.setdefault("errors", []).append(f"{name}: {type(e).__name__}: {e}"[:300])
        return default


def run(day, cfg, history_dir=None):
    ua = cfg["user_agent"]
    issue = f"{(date.fromisoformat(day) - date.fromisoformat(cfg['issue_epoch'])).days:03d}"
    now = datetime.now(timezone.utc)
    paper = {"date": day, "issue": issue, "weekday": date.fromisoformat(day).strftime("%A")}
    archive = {"generated_at": now.isoformat(), "dropped": []}
    sources = []

    # snow: Aspen seven plus one or more stations per region, one request
    aspen_ids = [s["id"] for s in cfg["aspen_snotel"]]
    region_ids = sorted({i for r in cfg["regions"] for i in r["snotel"]} - set(aspen_ids))
    names = {str(s["id"]): s["name"] for s in cfg["aspen_snotel"]} | cfg["snotel_names"]
    txt = get(snotel_url(aspen_ids + region_ids), ua, label="NRCS SNOTEL")
    raw = safely(archive, "snotel", lambda: parse_snotel_csv(txt) if txt else {}, {})
    stations, dropped = snotel_block(raw, aspen_ids, day, names)
    others, dropped2 = snotel_block(raw, region_ids, day, names)
    archive["dropped"] += dropped + dropped2
    if stations:
        indep = next((s for s in stations if s["id"] == 542), None)
        paper["snow"] = {"stations": stations, "median_depth_in": median_of(stations, "depth_in"),
                         "median_swe_in": median_of(stations, "swe_in"),
                         "new_24h_in": max(0, median_of(stations, "depth_24h_in") or 0) if any("depth_24h_in" in s for s in stations) else None,
                         "indep_swe_in": indep and indep["swe_in"], "indep_pct_median": indep and indep["pct_median"]}
        sources.append(f"NRCS SNOTEL {date.fromisoformat(day).day} {date.fromisoformat(day).strftime('%b')}")

    # forecast: Aspen summit point, alerts
    sp = cfg["summit_point"]
    fc = safely(archive, "nws summit", lambda: nws_forecast(sp["lat"], sp["lon"], ua))
    if fc:
        paper["summit"] = {"name": sp["name"], "elev_ft": sp["elev_ft"], "days": summit_days(fc), "next48h": next48(fc)}
        archive["forecast_calls"] = record_calls(fc, day, "NWS point, Aspen summit")
        sources.append(f"NWS {fmt_time(fc['issued'])}")
    alerts = safely(archive, "nws alerts", lambda: nws_alerts(sp["lat"], sp["lon"], ua), [])
    if alerts:
        paper["alerts"] = alerts

    # avalanche and regions
    zones = safely(archive, "caic", lambda: caic(ua), {})
    if zones:
        sources.append("CAIC via avalanche.org")
        archive["caic_zones"] = len(zones)
    by_id = {s["id"]: s for s in stations + others}
    regions = []
    for rg in cfg["regions"]:
        rows = [by_id[i] for i in rg["snotel"] if i in by_id]
        rec = {"name": rg["name"], "home": bool(rg.get("home"))}
        if rows:
            rec["pct_median"] = round(statistics.median([r["pct_median"] for r in rows if r["pct_median"] is not None])) \
                if any(r["pct_median"] is not None for r in rows) else None
            rec["new_24h_in"] = max(0, median_of(rows, "depth_24h_in") or 0) if any("depth_24h_in" in r for r in rows) else None
        rfc = fc if rg.get("home") else safely(archive, f"nws {rg['name']}", lambda: nws_forecast(rg["point"][0], rg["point"][1], ua))
        if rfc:
            rec["next48h"] = next48(rfc)["text"]
        lvl = caic_at(zones, rg["point"][0], rg["point"][1]) if zones else None
        if lvl:
            rec["avalanche"] = lvl
        rec["resorts"] = [r for r in (safely(archive, f"liftie {n}", lambda n=n: resort_status(n, cfg, day, ua)) for n in rg["resorts"]) if r]
        regions.append(rec)
    paper["regions"] = regions
    if any(r.get("status") == "Open" for rg in regions for r in rg["resorts"]):
        sources.append("Liftie lift status")

    # roads
    key = os.environ.get("CDOT_API_KEY")
    if key:
        roads = safely(archive, "cotrip", lambda: road_verdicts(cfg["routes"], road_features(key, ua), now), [])
        if roads:
            paper["roads"] = [{k: r[k] for k in ("route", "verdict", "reason")} for r in roads]
            archive["roads_matched"] = {r["route"]: r["matched"] for r in roads}
            sources.append(f"COtrip {fmt_time(now.isoformat())}")
            paper["cdot_notice"] = True

    # markets
    mk = [x for x in (safely(archive, f"market {m['name']}", lambda m=m: market(m, ua)) for m in cfg["markets"]) if x]
    if mk:
        paper["markets"] = mk
        sources.append("Yahoo Finance")

    # scorebook
    if history_dir:
        hist = [json.loads(p.read_text()) for p in sorted(Path(history_dir).glob("????-??-??.json")) if p.stem < day][-14:]
        archive["scores"] = safely(archive, "scores", lambda: score_calls(hist + [{"date": day, "paper": paper, "archive": archive}], day), [])

    paper["sources"] = sources
    news = safely(archive, "news", lambda: collect_news(cfg, day, ua, now), [])
    archive["news_candidates"] = len(news)
    archive["fetch_log"] = LOG
    return {"schema": 2, "paper": paper, "archive": archive}, news


# ---------------------------------------------------------------- validate
BANNED_UNITS = re.compile(r"\b\d+(\.\d+)?\s?(cm|mm|°C|km|hPa|mb)\b")


def validate(doc):
    errs = []
    p = doc.get("paper", {})
    for k in ("date", "issue", "weekday"):
        if not p.get(k):
            errs.append(f"missing {k}")
    if BANNED_UNITS.search(json.dumps(p, ensure_ascii=False)):
        errs.append("metric unit in paper fields")
    for s in p.get("snow", {}).get("stations", []):
        if s.get("swe_in") is not None and not 0 <= s["swe_in"] <= 80:
            errs.append(f"implausible SWE {s}")
        if s.get("depth_in") is not None and not 0 <= s["depth_in"] <= 250:
            errs.append(f"implausible depth {s}")
    for d in p.get("summit", {}).get("days", []):
        for k in ("high_f", "low_f"):
            if d.get(k) is not None and not -50 <= d[k] <= 100:
                errs.append(f"implausible {k} {d}")
    for r in p.get("roads", []):
        if r["verdict"] not in ("GO", "CAUTION", "NO-GO"):
            errs.append(f"bad verdict {r}")
    if "apiKey=" in json.dumps(doc) and "***" not in json.dumps(doc):
        errs.append("API key leaked")
    return errs


# ---------------------------------------------------------------- selftest (parsers, no network)
def selftest():
    csvtxt = ("#------ NRCS\n# Reporting Frequency: Daily\n"
              "Date,Station Id,Station Name,Snow Water Equivalent (in) Start of Day Values,"
              "Snow Depth (in) Start of Day Values,Snow Water Equivalent % of Median (1991-2020)\n"
              "2026-11-05,542,Independence Pass,2.5,13,\n2026-11-06,542,Independence Pass,2.4,11,126\n"
              "2026-11-05,737,Schofield Pass,4.1,18,\n2026-11-06,737,Schofield Pass,4.1,16,146\n"
              "2026-11-06,380,Wrong Station,1.0,5,80\n")
    raw = parse_snotel_csv(csvtxt)
    st, dropped = snotel_block(raw, [542, 737, 380], "2026-11-06", {"542": "Independence Pass", "737": "Schofield Pass", "380": "Butte"})
    assert st[0] == {"id": 542, "name": "Independence Pass", "swe_in": 2.4, "depth_in": 11.0, "pct_median": 126,
                     "swe_24h_in": -0.1, "depth_24h_in": -2.0}, st[0]
    assert dropped and dropped[0]["got"] == "Wrong Station"
    cases = {
        "Snow likely. New snow accumulation of 2 to 4 inches possible.": ("2–4 in", 2, 4),
        "New snow accumulation of less than one inch possible.": ("under 1 in", 0, 1),
        "New snow accumulation of less than half an inch possible.": ("under ½ in", 0, 0.5),
        "New snow accumulation of around one inch possible.": ("about 1 in", 1, 1),
        "Little or no snow accumulation expected.": ("0 in", 0, 0),
        "Sunny, with a high near 41.": None,
    }
    for t, want in cases.items():
        got = snow_band(t)
        assert (got is None and want is None) or (got[0] == want[0] and got[1] == want[1] and got[2] == want[2]), (t, got)
    fc = {"issued": "2026-11-04T10:23:00+00:00", "periods": [
        {"name": "Today", "start": "2026-11-04T06:00:00-07:00", "end": "", "day": True, "temp_f": 30, "pop_pct": 80, "band": ("about 1 in", 1, 1)},
        {"name": "Tonight", "start": "2026-11-04T18:00:00-07:00", "end": "", "day": False, "temp_f": 12, "pop_pct": 90, "band": ("2–4 in", 2, 4)},
        {"name": "Thursday", "start": "2026-11-05T06:00:00-07:00", "end": "", "day": True, "temp_f": 25, "pop_pct": 20, "band": None},
        {"name": "Thursday Night", "start": "2026-11-05T18:00:00-07:00", "end": "", "day": False, "temp_f": 8, "pop_pct": 0, "band": None}]}
    assert next48(fc) == {"text": "2–4 in", "low_in": 2, "high_in": 4, "when": "Tonight"}
    d = summit_days(fc)
    assert d[0] == {"date": "2026-11-04", "day": "Wed", "high_f": 30, "snow_day": "about 1 in", "pop_pct": 90, "low_f": 12, "snow_night": "2–4 in"}, d[0]
    calls = record_calls(fc, "2026-11-04", "NWS point")
    hist = [{"date": "2026-11-04", "paper": {"snow": {"stations": [{"id": i, "depth_in": 5} for i in range(7)]}}, "archive": {"forecast_calls": calls}},
            {"date": "2026-11-05", "paper": {"snow": {"stations": [{"id": i, "depth_in": 5 + g} for i, g in enumerate([6, 7, 8, 8, 9, 3, 10])]}}, "archive": {}}]
    sc = score_calls(hist, "2026-11-05")
    assert sc[0]["observed_in"] == 8 and sc[0]["verdict"] == "low" and sc[0]["low_in"] == 3 and sc[0]["high_in"] == 5, sc
    feats = [{"feed": "incidents", "route": _route_key("CO 82"), "mps": [51.4, 68.5], "props": {},
              "text": "Safety closure between Mile Point 51.4 and 68.5"},
             {"feed": "plannedEvents", "route": _route_key("I-70"), "mps": [253, 262], "props": {}, "text": "Shoulder closures for sign repair"}]
    rv = {r["route"]: r for r in road_verdicts([{"name": "Indy", "segments": [["CO82", 42, 85]]},
                                                {"name": "Denver", "segments": [["CO82", 0, 30], ["I70", 116, 260]]},
                                                {"name": "Snowmass", "segments": [["CO82", 30, 42]]}], feats, datetime.now(timezone.utc))}
    assert rv["Indy"]["verdict"] == "NO-GO" and rv["Indy"]["reason"] == "Closed MP 51.4 to 68.5", rv["Indy"]
    assert rv["Denver"]["verdict"] == "CAUTION", rv["Denver"]
    assert rv["Snowmass"]["verdict"] == "GO"
    assert _route_key("CO-82") == _route_key("SH 82") == "CO82" and _route_key("I-070") == "I70"
    assert validate({"paper": {"date": "x", "issue": "1", "weekday": "y", "note": "12 cm"}}) == ["metric unit in paper fields"]
    rss = ('<?xml version="1.0"?><rss version="2.0"><channel><title>x</title>'
           '<item><title>Fed holds &amp; signals patience</title><link>https://example.org/a</link>'
           '<pubDate>Fri, 06 Nov 2026 12:00:00 GMT</pubDate><description>&lt;p&gt;The Fed held rates.&lt;/p&gt;</description></item>'
           '<item><title>Old story</title><link>https://example.org/b</link><pubDate>Mon, 02 Nov 2026 12:00:00 GMT</pubDate></item>'
           '</channel></rss>')
    atom = ('<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Chip rout</title>'
            '<link href="https://example.org/c"/><updated>2026-11-06T08:00:00Z</updated><summary>Stocks fell.</summary></entry></feed>')
    r = parse_feed(rss)
    assert r[0]["title"] == "Fed holds & signals patience" and r[0]["summary"] == "The Fed held rates.", r[0]
    a2 = parse_feed(atom)
    assert a2[0]["url"] == "https://example.org/c" and a2[0]["published"].hour == 8
    global get
    real_get = get
    try:
        get = lambda url, ua, accept=None, label=None: rss if "rss" in url else atom
        got = collect_news({"news_feeds": [{"outlet": "T", "url": "https://t/rss", "section": "economy"},
                                           {"outlet": "A", "url": "https://t/atom", "section": "markets"}]},
                           "2026-11-06", "ua", now=datetime(2026, 11, 6, 13, 0, tzinfo=timezone.utc))
    finally:
        get = real_get
    assert [g["title"] for g in got] == ["Fed holds & signals patience", "Chip rout"], got
    sq = [[(-107.5, 38.8), (-106.5, 38.8), (-106.5, 39.5), (-107.5, 39.5), (-107.5, 38.8)]]
    zs = [([sq], "Considerable"), ([[[(-106.0, 39.5), (-105.5, 39.5), (-105.5, 40.0), (-106.0, 40.0)]]], "Low")]
    assert caic_at(zs, 39.1514, -106.8186) == "Considerable" and caic_at(zs, 39.7, -105.8) == "Low" and caic_at(zs, 37.5, -106.8) is None
    print("selftest: all parser checks passed")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--date", default=datetime.now(MT).date().isoformat())
    r.add_argument("--out", required=True)
    r.add_argument("--history")
    v = sub.add_parser("validate")
    v.add_argument("path")
    sub.add_parser("selftest")
    h = sub.add_parser("headlines", help="one line per candidate story, for the writer to choose from")
    h.add_argument("path")
    h.add_argument("--hint")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "headlines":
        for i, n in enumerate(json.loads(Path(a.path).read_text())):
            if not a.hint or n["hint"] == a.hint:
                print(f"{i:>3} {n['published'][5:16]} {n['hint']:<10} {n['outlet']:<14} {n['title']}")
        return
    if a.cmd == "validate":
        errs = validate(json.loads(Path(a.path).read_text()))
        print("\n".join(errs) or "valid")
        sys.exit(1 if errs else 0)
    cfg = json.loads((HERE / "config.json").read_text())
    doc, news = run(a.date, cfg, a.history)
    errs = validate(doc)
    if not cfg.get("news_summaries", True):  # public repo: keep titles and links, not outlets' text
        news = [{k: v for k, v in n.items() if k != "summary"} for n in news]
    news_path = Path(a.out).with_name(f"news-{a.date}.json")
    news_path.write_text(json.dumps(news, indent=0, ensure_ascii=False))
    doc["archive"]["validation"] = errs
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    ok = sum(1 for x in LOG if x["status"] == "ok")
    print(f"wrote {a.out} and {news_path.name}: {ok}/{len(LOG)} fetches ok; {len(news)} stories; {len(errs)} validation issues")


if __name__ == "__main__":
    main()
