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


# ---------------------------------------------------------------- roads (COtrip official feeds)
CLOSED_TXT = re.compile(r"\b(road|highway|pass|safety|full|seasonal)\s+closure\b|\broad (is )?closed\b|\bclosed (in )?both directions\b|"
                        r"\ball lanes (are )?closed\b|\bclosed to (all|through) traffic\b|\bchain law\b", re.I)


def _route_key(s):
    """'US-160E', 'CO 82', 'I-70W', 'SH 82' -> 'US160', 'CO82', 'I70', 'CO82'."""
    s = re.sub(r"[^A-Z0-9]", "", str(s).upper()).replace("INTERSTATE", "I").replace("STATEHIGHWAY", "CO")
    s = re.sub(r"^SH(?=\d)", "CO", s)
    s = re.sub(r"(\d)[NSEW]$", r"\1", s)
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


def _mp_range(pr):
    vals = [num(pr.get(k)) for k in ("marker", "startMarker", "endMarker", "primaryMP", "secondaryMP") if num(pr.get(k)) is not None]
    return (min(vals), max(vals)) if vals else None


def _ts(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v / 1000, timezone.utc)
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None


def _active_window(start, end, now):
    s, e = _ts(start), _ts(end)
    return (s is None or s <= now) and (e is None or e >= now)


def classify(feed, pr, now):
    """One COtrip record -> (verdict, reason) or None when it is not active or says nothing about driving."""
    rng = _mp_range(pr)
    where = (f"MP {rng[0]:g}" if rng[0] == rng[1] else f"MP {round(rng[0], 1):g} to {round(rng[1], 1):g}") if rng else ""
    if feed == "roadConditions":
        try:
            conds = json.loads(pr.get("currentConditions") or "[]")
        except (TypeError, json.JSONDecodeError):
            conds = []
        desc = [re.sub(r"^\d+\s*-\s*", "", c.get("conditionDescription", "")).strip().lower() for c in conds
                if _active_window(c.get("startTime"), c.get("endTime"), now)]
        desc = [d for d in desc if d and "forecast" not in d]
        if any("closed" in d or "chain law" in d for d in desc):
            return "NO-GO", f"Closed {where}".strip()
        bad = [d for d in desc if re.search(r"ic[ey]|snow|slush|pack|traction|spots|fog|blowing", d)]
        if bad:
            return "CAUTION", f"{bad[0].capitalize()} {where}".strip()
        if desc:
            return "GO", desc[0].capitalize()
        return None
    if feed == "plannedEvents":
        sched = pr.get("schedule") or []
        if sched and not any(_active_window(x.get("startTime"), x.get("endTime"), now) for x in sched):
            return None
    text = " ".join(_flat({k: v for k, v in pr.items() if k in ("type", "travelerInformationMessage", "name")}))
    lanes = pr.get("laneImpacts") or []
    all_closed = any(str(l.get("laneClosures", "0")) != "0" and l.get("laneCount") and
                     sum("lane" in t for t in l.get("closedLaneTypes", [])) >= l["laneCount"] for l in lanes)
    if CLOSED_TXT.search(text) or all_closed or "closure" in str(pr.get("type", "")).lower():
        return "NO-GO", f"Closed {where}".strip()
    lane_hit = any(any("lane" in t for t in l.get("closedLaneTypes", [])) for l in lanes)
    if lane_hit or re.search(r"alternating traffic|delays|crash|flood|rock ?fall|ic[ey]|snow", text, re.I):
        kind = str(pr.get("type") or "Delays").strip()
        return "CAUTION", f"{kind} {where}".strip()
    return None


def road_features(key, ua):
    feats = []
    for feed in ("incidents", "plannedEvents"):
        js = get_json(f"https://data.cotrip.org/api/v1/{feed}?apiKey={key}", ua, f"COtrip {feed}")
        if js is None:
            raise RuntimeError(f"COtrip {feed} did not load")
        for f in js.get("features", []):
            pr = f.get("properties", {})
            feats.append({"feed": feed, "route": _route_key(pr.get("routeName", "")), "range": _mp_range(pr), "props": pr})
    return feats


RANK = {"GO": 0, "CAUTION": 1, "NO-GO": 2}


def road_verdicts(routes, feats, now):
    if not feats:
        return []
    out = []
    for rt in routes:
        worst, n, seen_cond = None, 0, False
        for rk, lo, hi in rt["segments"]:
            for f in feats:
                if f["route"] != _route_key(rk) or not f["range"] or max(lo, f["range"][0]) > min(hi, f["range"][1]):
                    continue
                c = classify(f["feed"], f["props"], now)
                if not c:
                    continue
                n += 1
                seen_cond |= f["feed"] == "roadConditions"
                if worst is None or RANK[c[0]] > RANK[worst[0]]:
                    worst = c
        if worst is None:
            worst = ("GO", "Open, no incidents reported")
        out.append({"route": rt["name"], "verdict": worst[0], "reason": worst[1], "matched": n})
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
        rec.setdefault("date", rec.get("paper", {}).get("date"))
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
    names = {str(s["id"]): s["name"] for s in cfg["aspen_snotel"]}
    txt = get(snotel_url(aspen_ids), ua, label="NRCS SNOTEL Aspen")
    raw = safely(archive, "snotel", lambda: parse_snotel_csv(txt) if txt else {}, {})
    stations, dropped = snotel_block(raw, aspen_ids, day, names)
    archive["dropped"] += dropped
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

    # avalanche, Aspen's mountains, and mountains across Colorado
    zones = safely(archive, "caic", lambda: caic(ua), [])
    if zones:
        sources.append("CAIC via avalanche.org")
        archive["caic_zones"] = len(zones)
    status = lambda m: ("Opens today" if m.get("opens") == day else
                        f"Opens {date.fromisoformat(m['opens']).day} {date.fromisoformat(m['opens']).strftime('%b')}" if m.get("opens", "") > day else None)

    def outlook(m):
        f = fc if m["name"] == "Aspen Mountain" and fc else safely(archive, f"nws {m['name']}", lambda: nws_forecast(m["point"][0], m["point"][1], ua))
        return next48(f)["text"] if f else None

    paper["aspen_mountains"] = [{k: v for k, v in {"name": m["name"], "status": status(m), "next48h": outlook(m)}.items() if v is not None}
                                for m in cfg["aspen_mountains"]]
    ids = [m["snotel"] for m in cfg["mountains"] if m.get("snotel")]
    txt2 = get(snotel_url(ids), ua, label="NRCS SNOTEL mountains")
    raw2 = safely(archive, "snotel mountains", lambda: parse_snotel_csv(txt2) if txt2 else {}, {})
    sites, bad = snotel_block(raw2, ids, day, {str(m["snotel"]): m["snotel_name"] for m in cfg["mountains"] if m.get("snotel")})
    archive["dropped"] += bad
    by_id = {x["id"]: x for x in sites}
    rows = []
    for m in cfg["mountains"]:
        site = by_id.get(m.get("snotel"), {})
        row = {"name": m["name"], "region": m["region"], "status": status(m), "depth_in": site.get("depth_in"),
               "depth_24h_in": site.get("depth_24h_in"), "pct_median": site.get("pct_median"), "next48h": outlook(m),
               "avalanche": caic_at(zones, m["point"][0], m["point"][1]) if zones else None}
        rows.append({k: v for k, v in row.items() if v is not None})
    paper["mountains"] = rows
    if zones:
        paper["avalanche_aspen"] = caic_at(zones, sp["lat"], sp["lon"])

    # roads
    key = os.environ.get("CDOT_API_KEY")
    roads = safely(archive, "cotrip", lambda: road_verdicts(cfg["routes"], road_features(key, ua), now), []) if key else []
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
    now = datetime(2026, 11, 8, 13, 0, tzinfo=timezone.utc)
    ms = lambda d: int(d.timestamp() * 1000)
    cond = lambda txt: json.dumps([{"conditionDescription": txt, "startTime": ms(now) - 3600000, "endTime": ms(now) + 3600000},
                                   {"conditionDescription": "forecast text included", "startTime": ms(now), "endTime": ms(now) + 1}])
    feats = [{"feed": "incidents", "route": _route_key("CO-82E"), "range": (51.4, 68.5),
              "props": {"type": "Safety Closure", "travelerInformationMessage": "Between Difficult Campground and Twin Lakes from Mile Point 51.4 to Mile Point 68.5. Road closed.",
                        "startMarker": 51.4, "endMarker": 68.5, "laneImpacts": []}},
             {"feed": "roadConditions", "route": _route_key("CO 82"), "range": (30.1, 41.9), "props": {"currentConditions": cond("4 - wet"), "primaryMP": 30.1, "secondaryMP": 41.9}},
             {"feed": "plannedEvents", "route": _route_key("I-70W"), "range": (253.0, 262.0),
              "props": {"type": "Road Construction", "travelerInformationMessage": "The right lane is closed.", "startMarker": 253, "endMarker": 262,
                        "schedule": [{"startTime": "2026-11-08T12:00:00Z", "endTime": "2026-11-08T23:00:00Z"}],
                        "laneImpacts": [{"direction": "west", "laneCount": 2, "laneClosures": "2001", "closedLaneTypes": ["right lane"]}]}},
             {"feed": "roadConditions", "route": _route_key("US 160"), "range": (150.0, 190.0), "props": {"currentConditions": cond("2 - icy spots"), "primaryMP": 150, "secondaryMP": 190}}]
    rv = {r["route"]: r for r in road_verdicts([{"name": "Indy", "segments": [["CO82", 42, 85]]},
                                                {"name": "Snowmass", "segments": [["CO82", 30, 42]]},
                                                {"name": "Denver", "segments": [["CO82", 0, 30], ["I70", 116, 260]]},
                                                {"name": "Wolf", "segments": [["US160", 150, 190]]},
                                                {"name": "Red", "segments": [["US550", 60, 95]]}], feats, now)}
    assert rv["Indy"]["verdict"] == "NO-GO" and rv["Indy"]["reason"] == "Closed MP 51.4 to 68.5", rv["Indy"]
    assert rv["Snowmass"]["verdict"] == "GO" and rv["Snowmass"]["reason"] == "Wet", rv["Snowmass"]
    assert rv["Denver"]["verdict"] == "CAUTION" and rv["Denver"]["reason"].startswith("Road Construction"), rv["Denver"]
    assert rv["Wolf"]["verdict"] == "CAUTION" and rv["Wolf"]["reason"] == "Icy spots MP 150 to 190", rv["Wolf"]
    assert rv["Red"]["verdict"] == "GO" and rv["Red"]["reason"] == "Open, no incidents reported", rv["Red"]
    assert _route_key("CO-82") == _route_key("SH 82") == _route_key("CO 82") == "CO82" and _route_key("I-070W") == "I70" and _route_key("US-160E") == "US160"
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
    cs = sub.add_parser("cotrip-sample", help="save a trimmed sample of COtrip records on Aspen routes, for checking the road parser")
    cs.add_argument("out")
    h = sub.add_parser("headlines", help="one line per candidate story, for the writer to choose from")
    h.add_argument("path")
    h.add_argument("--hint")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "cotrip-sample":
        key, ua = os.environ.get("CDOT_API_KEY"), json.loads((HERE / "config.json").read_text())["user_agent"]
        out = {}
        for feed in ("incidents", "plannedEvents"):
            js = get_json(f"https://data.cotrip.org/api/v1/{feed}?apiKey={key}", ua, f"COtrip {feed}") if key else None
            feats = (js or {}).get("features", [])
            trim = lambda v: v[:240] if isinstance(v, str) else v
            keep = [f for f in feats if any(t in json.dumps(f.get("properties", {})) for t in ("82", "I-70", "160", "133", "550"))][:12]
            out[feed] = {"top_keys": sorted(k for k in (js or {}) if k != "features"),
                         "top_meta": {k: v for k, v in (js or {}).items() if k != "features" and not isinstance(v, (list, dict))},
                         "total": len(feats), "first_keys": sorted((feats[0].get("properties") or {}).keys()) if feats else [],
                         "sample": [{k: (trim(v) if not isinstance(v, (dict, list)) else json.loads(json.dumps(v)[:600] + "\"" * 0) if len(json.dumps(v)) < 600 else json.dumps(v)[:600])
                                     for k, v in (f.get("properties") or {}).items()} for f in keep]}
        Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False))
        return
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
