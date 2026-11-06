#!/usr/bin/env python3
"""Morning Brief renderer: data JSON (numbers, from fetch.py) + edition JSON (words, from the daily task)
-> two-page US Letter PDF in the locked template.

    python3 render.py --data data/2026-11-06.json --edition edition/2026-11-06.json --out out/Morning-Brief-2026-11-06.pdf

Refuses to render when the words break the style guide (word limits, parentheses, banned words,
metric units) and fails when anything overflows its page. Exit 2 = words to fix, exit 3 = layout overflow.
Needs jinja2 and Playwright (Chromium).
"""
import argparse, json, re, sys
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

HERE = Path(__file__).resolve().parent
TPL = HERE / "template"

# Slot word limits: (min words, max words).
LIMITS = {
    "headline": (4, 12), "verdict": (12, 40), "sponsor": (0, 6), "brief": (20, 40),
    "lead.head": (4, 12), "lead.text": (35, 60), "lead.outlet": (1, 3),
    "item.lead": (1, 5), "item.text": (8, 24), "item.outlet": (1, 3),
    "week.day": (1, 3), "week.text": (3, 16),
    "longread.title": (2, 14), "longread.why": (6, 26), "longread.outlet": (1, 3),
    "pick.title": (1, 10), "pick.why": (0, 18), "pick.when": (1, 5), "pick.place": (1, 6),
    "events.title": (1, 8), "events.place": (1, 6), "events.day": (1, 2), "events.time": (0, 3),
    "ongoing.title": (1, 8), "ongoing.place": (1, 6), "ongoing.until": (1, 4),
    "coming.title": (1, 8), "coming.when": (1, 5), "coming.place": (1, 6), "resort_status": (1, 4),
}
# News sections: key, printed head, (min, max) stories. Page 2 is the same every day; page 3 changes at weekends.
PAGE2 = [("markets", "markets", (2, 3)), ("world", "world", (3, 4)), ("us", "us & politics", (3, 4)),
         ("economy", "economy & central banks", (2, 3)), ("europe", "europe & uk", (2, 3))]
PAGE3 = {"daily": [("companies", "companies", (3, 4)), ("financials", "financials & market structure", (2, 3)),
                   ("tech", "tech & ai", (3, 4)), ("asia", "asia-pacific", (2, 3)),
                   ("mideast", "middle east & energy", (2, 3)), ("science", "science, health & climate", (1, 2))],
         "weekend": [("review", "the week in review", (4, 6)), ("opinion", "opinion & ideas", (2, 3)),
                     ("longreads", "long reads", (2, 3)), ("arts", "arts & books", (2, 3)),
                     ("living", "travel, food & living", (1, 2)), ("weekendbiz", "business & tech weekend", (2, 3))]}
COUNTS = {"week": {"daily": (3, 6), "weekend": (0, 6)}, "events": (0, 18), "ongoing": (0, 3), "coming": (0, 3)}
BANNED = re.compile(r"\b(leverage|synergy|unlock|in today's landscape|it's important to note|stale|unconfirmed|per the)\b"
                    r"|(?<!\w)est\.", re.I)
METRIC = re.compile(r"\b\d+(\.\d+)?\s?(cm|mm|°C|km|hPa|mb)\b")
PAYWALLED = re.compile(r"(^|\.)(ft\.com|nytimes\.com|wsj\.com|bloomberg\.com|economist\.com|barrons\.com|washingtonpost\.com|"
                       r"theinformation\.com|fortune\.com|forbes\.com|businessinsider\.com|seekingalpha\.com|telegraph\.co\.uk|"
                       r"thetimes\.co\.uk|bostonglobe\.com|asia\.nikkei\.com|risk\.net)$")
CDOT_NOTICE = ("The data made available here has been modified for use from its original source, which is the State of "
               "Colorado, Department of Transportation (CDOT). THE STATE OF COLORADO AND CDOT MAKES NO REPRESENTATIONS OR "
               "WARRANTY AS TO THE COMPLETENESS, ACCURACY, TIMELINESS, OR CONTENT OF ANY DATA MADE AVAILABLE THROUGH THIS "
               "SITE. THE STATE OF COLORADO AND CDOT EXPRESSLY DISCLAIMS ALL WARRANTIES, WHETHER EXPRESS OR IMPLIED, "
               "INCLUDING ANY IMPLIED WARRANTIES OF MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE. The data is "
               "subject to change as modifications and updates are complete. It is understood that the information "
               "contained in the Web feed is being used at one's own risk.")


def words(s):
    return len(re.findall(r"[\w'’%°½–$.,-]+", s or ""))


def kind_of(day):
    return "weekend" if date.fromisoformat(day).weekday() >= 5 else "daily"


def check_edition(e, day):
    """Return a list of style violations. Empty list = publishable words."""
    errs, kind = [], kind_of(day)

    def slot(name, text, required=True):
        lo, hi = LIMITS[name]
        text = text or ""
        if not text:
            if required and lo:
                errs.append(f"{name}: missing")
            return
        n = words(text)
        if not lo <= n <= hi:
            errs.append(f"{name}: {n} words, limit {lo}–{hi}: {text!r}")
        if re.search(r"[()\[\]]", text):
            errs.append(f"{name}: parentheses are not allowed: {text!r}")
        if BANNED.search(text):
            errs.append(f"{name}: banned wording '{BANNED.search(text).group(0)}': {text!r}")
        if METRIC.search(text):
            errs.append(f"{name}: metric unit: {text!r}")
        if re.search(r"https?://", text):
            errs.append(f"{name}: URL in text; put it in the url field")

    def link(where, url):
        if not str(url or "").startswith("https://"):
            errs.append(f"{where}: needs an https link")
            return
        host = re.sub(r"^https://([^/]+).*", r"\1", url).lower()
        if PAYWALLED.search(host):
            errs.append(f"{where}: paywalled outlet {host}")

    def count(name, items, lo, hi):
        if not lo <= len(items) <= hi:
            errs.append(f"{name}: {len(items)} items, allowed {lo}–{hi}")

    for k in ("headline", "verdict", "brief"):
        slot(k, e.get(k))
    for name, st in (e.get("resort_status") or {}).items():
        slot("resort_status", st)
    slot("sponsor", e.get("sponsor"), required=False)
    lead = e.get("lead") or {}
    for f in ("head", "text", "outlet"):
        slot(f"lead.{f}", lead.get(f))
    link("lead", lead.get("url"))
    secs = e.get("sections") or {}
    wanted = [k for k, _, _ in PAGE2 + PAGE3[kind]]
    for k in secs:
        if k not in wanted:
            errs.append(f"sections.{k}: not a {kind} section; use {', '.join(wanted)}")
    for k, _, (lo, hi) in PAGE2 + PAGE3[kind]:
        if kind == "weekend" and k == "markets":
            lo = 0
        items = secs.get(k) or []
        count(f"sections.{k}", items, lo, hi)
        for i, it in enumerate(items):
            for f in ("lead", "text", "outlet"):
                slot(f"item.{f}", it.get(f))
            link(f"sections.{k}[{i}]", it.get("url"))
            if it.get("url2"):
                link(f"sections.{k}[{i}].url2", it["url2"])
    count("week", e.get("week") or [], *COUNTS["week"][kind])
    for w in e.get("week") or []:
        slot("week.day", w.get("day"))
        slot("week.text", w.get("text"))
    lr = e.get("longread")
    if kind == "daily" and not lr:
        errs.append("longread: missing")
    if lr:
        for f in ("title", "why", "outlet"):
            slot(f"longread.{f}", lr.get(f))
        link("longread", lr.get("url"))
    if e.get("pick"):
        for f in ("title", "why", "when", "place"):
            slot(f"pick.{f}", e["pick"].get(f), required=f != "why")
        link("pick", e["pick"].get("url"))
    for group, fields in (("events", ("title", "place", "day", "time")), ("ongoing", ("title", "place", "until")),
                          ("coming", ("title", "when", "place"))):
        items = e.get(group) or []
        count(group, items, *COUNTS[group])
        for it in items:
            for f in fields:
                slot(f"{group}.{f}", it.get(f), required=f != "time")
            link(group, it.get("url"))
            if group == "events" and it.get("label") not in ("FREE", "NO FEE LISTED"):
                errs.append(f"events: label must be FREE or NO FEE LISTED: {it.get('title')}")
    return errs


# ---------------------------------------------------------------- formatting helpers
def inch(v):
    if v is None:
        return ""
    return f"{v:g} in" if isinstance(v, (int, float)) else str(v)


def signed(v, unit=" in"):
    if v is None:
        return ""
    return "0" + unit if v == 0 else f"{v:+g}{unit}".replace("-", "−")


def money(m):
    v = m["value"]
    if m["fmt"] == "yield":
        return f"{v:.2f}%"
    if m["fmt"] == "fx":
        return f"${v:.4f}"
    if m["fmt"] == "usd":
        return f"${v:,.0f}" if v >= 1000 else f"${v:,.2f}"
    return f"{v:,.0f}" if v >= 10000 else f"{v:,.2f}"


def change(m):
    if m.get("change_bp") is not None:
        return f"{m['change_bp']:+d} bp".replace("-", "−")
    if m.get("change_pct") is not None:
        return f"{m['change_pct']:+.1f}%".replace("-", "−")
    return ""


def chg_sign(m):
    v = m.get("change_pct", m.get("change_bp"))
    return 0 if v is None else (1 if v > 0 else (-1 if v < 0 else 0))


def as_of_text(m, today):
    d = m.get("as_of")
    if not d:
        return ""
    dd = date.fromisoformat(d)
    if m["fmt"] == "index":
        return f"{dd.strftime('%a')} close"
    return "today" if dd == date.fromisoformat(today) else f"{dd.strftime('%a')} latest"


SHAPES = [  # Bauhaus compositions, rotated by issue number so the masthead varies but never degrades
    '<rect x="0" y="62" width="170" height="12" fill="#121212"/><circle cx="118" cy="44" r="40" fill="#D7261E"/>'
    '<rect x="132" y="24" width="56" height="56" fill="#1C4E9C"/><polygon points="196,74 226,74 211,8" fill="#F2B705"/>',
    '<circle cx="60" cy="40" r="38" fill="#F2B705"/><rect x="82" y="18" width="62" height="62" fill="#D7261E"/>'
    '<rect x="0" y="66" width="226" height="8" fill="#121212"/><circle cx="196" cy="38" r="22" fill="none" stroke="#121212" stroke-width="5"/>',
    '<polygon points="20,74 92,74 56,4" fill="#1C4E9C"/><circle cx="140" cy="42" r="34" fill="#D7261E"/>'
    '<rect x="168" y="10" width="44" height="64" fill="#121212"/><rect x="0" y="70" width="226" height="4" fill="#121212"/>',
    '<rect x="10" y="10" width="64" height="64" fill="#121212"/><circle cx="104" cy="42" r="32" fill="#1C4E9C"/>'
    '<polygon points="140,74 210,74 175,14" fill="#D7261E"/><circle cx="206" cy="20" r="12" fill="#F2B705"/>',
]


def composition(issue):
    return f'<svg viewBox="0 0 226 78" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{SHAPES[int(issue) % len(SHAPES)]}</svg>'


def build_tiles(p):
    snow, summit = p.get("snow") or {}, p.get("summit") or {}
    roads = {r["route"]: r for r in p.get("roads") or []}
    t = []
    if snow.get("new_24h_in") is not None:
        t.append({"label": "new snow, 24h", "value": inch(snow["new_24h_in"]), "caption": "Median of seven Aspen-area sites"})
    n48 = summit.get("next48h")
    if n48:
        val = "None" if n48["text"] == "none" else n48["text"]
        when = f", {n48['when'].lower()}" if n48.get("when") else ""
        t.append({"label": "next 48h", "value": val, "caption": f"{n48.get('label', 'NWS, Aspen summit')}{when}"})
    if snow.get("indep_pct_median") is not None:
        t.append({"label": "snowpack", "value": f"{snow['indep_pct_median']}%",
                  "caption": f"Of median at Independence Pass, {inch(snow.get('indep_swe_in'))} of water"})
    elif snow.get("indep_swe_in") is not None:
        t.append({"label": "snowpack", "value": inch(snow["indep_swe_in"]), "caption": "Water in the snow at Independence Pass"})
    ip = roads.get("Independence Pass")
    if ip:
        t.append({"label": "independence pass", "value": {"NO-GO": "Closed", "CAUTION": "Caution", "GO": "Open"}[ip["verdict"]],
                  "caption": ip["reason"]})
    home = next((r for r in p.get("regions") or [] if r.get("home")), {})
    if home.get("avalanche"):
        t.append({"label": "avalanche", "value": home["avalanche"], "caption": "Aspen zone danger, CAIC"})
    return t[:4]


def snow_columns(stations):
    cols = [("depth_in", "Depth", lambda v: f"{v:g}"), ("depth_24h_in", "24h", lambda v: signed(v, "")),
            ("swe_in", "Water", lambda v: f"{v:.1f}"), ("pct_median", "Of median", lambda v: f"{v}%")]
    out = []
    for key, head, f in cols:
        if any(s.get(key) is not None for s in stations):
            out.append({"head": head, "fmt": (lambda s, key=key, f=f: "" if s.get(key) is None else f(s[key]))})
    return out


def region_columns(regions):
    cols = [("pct_median", "Snowpack", lambda v: f"{v}%"), ("new_24h_in", "New 24h", inch),
            ("next48h", "Next 48h", lambda v: "None" if v == "none" else v), ("avalanche", "Avalanche", str)]
    return [{"head": h, "fmt": (lambda r, k=k, f=f: "" if r.get(k) is None else f(r[k]))}
            for k, h, f in cols if any(r.get(k) is not None for r in regions)]


def status_text(r):
    if r.get("status") == "Open" and r.get("lifts_total"):
        return f"Open, {r['lifts_open']} of {r['lifts_total']} lifts"
    return r.get("status", "")


def context(doc, e):
    p = doc["paper"]
    d = date.fromisoformat(p["date"])
    over = e.get("resort_status") or {}
    for rg in p.get("regions") or []:
        rg["resorts"] = [dict(r, status=over.get(r["name"], r.get("status"))) for r in rg.get("resorts", [])]
    regions = []
    for rg in p.get("regions") or []:
        rr = dict(rg)
        opened = [r["name"] for r in rg.get("resorts", []) if r.get("status") == "Open"]
        rr["open_text"] = ", ".join(opened)
        regions.append(rr)
    home = next((r for r in p.get("regions") or [] if r.get("home")), {})
    aspen_resorts = [dict(r, status_text=status_text(r)) for r in home.get("resorts", []) if r.get("status")]
    nxt = [r for r in aspen_resorts if r["status"].startswith("Opens")]
    aspen_open = None
    if nxt and not any(r["status"].startswith("Open,") or r["status"] == "Open" for r in aspen_resorts):
        aspen_open = f"{nxt[0]['name']} {nxt[0]['status'].replace('Opens', 'opens')}"
    avy = [f"{r['name']} {r['avalanche']}" for r in regions if r.get("avalanche")]
    levels = {r.get("avalanche") for r in regions if r.get("avalanche")}
    avy_line = (f"{levels.pop()} danger statewide." if len(levels) == 1 and len(avy) > 3 else " · ".join(avy)) if avy else None
    for m in p.get("markets") or []:
        m["as_of_text"] = as_of_text(m, p["date"])
    def start_min(t):
        m = re.match(r"\s*(\d{1,2})(?::(\d\d))?\s*(?:[–-]\s*\d{1,2}(?::\d\d)?\s*)?(am|pm|noon)?", t or "")
        if not m:
            return 24 * 60
        h, mm, ap = int(m.group(1)), int(m.group(2) or 0), m.group(3)
        if not ap:  # "5–7pm": take the meridiem from the end of the range
            ap = "pm" if re.search(r"pm", t or "") else "am"
        return (h % 12 + (12 if ap == "pm" else 0)) * 60 + mm
    order = list(dict.fromkeys(ev["day"] for ev in e.get("events") or []))
    ordered = sorted(e.get("events") or [], key=lambda ev: (order.index(ev["day"]), start_min(ev.get("time"))))
    evs, last = [], None
    for ev in ordered:
        ev = dict(ev, first=ev["day"] != last)
        last = ev["day"]
        evs.append(ev)
    e = dict(e, events=evs)
    kind = kind_of(p["date"])
    shapes = ["mc", "ms", "mt"]
    page2 = [{"key": k, "head": h, "shape": shapes[i % 3], "items": (e.get("sections") or {}).get(k) or []}
             for i, (k, h, _) in enumerate(PAGE2)]
    page3 = [{"key": k, "head": h, "shape": shapes[(i + 1) % 3], "items": (e.get("sections") or {}).get(k) or []}
             for i, (k, h, _) in enumerate(PAGE3[kind])]
    return {
        "kind": kind, "page2": [x for x in page2 if x["items"]], "page3": [x for x in page3 if x["items"]],
        "p": p, "e": e, "css": (TPL / "style.css").read_text(), "comp": composition(p["issue"]),
        "long_date": f"{d.strftime('%A')} {d.day} {d.strftime('%B %Y')}", "short_date": f"{d.day} {d.strftime('%b %Y')}",
        "tiles": build_tiles(p), "aspen_resorts": aspen_resorts, "aspen_open": aspen_open,
        "any_resort_snow": any(r.get("new_24h_in") is not None or r.get("base_in") is not None for r in aspen_resorts),
        "snow_cols": snow_columns((p.get("snow") or {}).get("stations", [])),
        "regions": regions, "region_cols": region_columns(regions), "avy_line": avy_line,
        "inch": inch, "money": money, "change": change, "chg_sign": chg_sign, "cdot_notice": CDOT_NOTICE,
    }


def render(doc, e, out_pdf, html_out=None):
    env = Environment(loader=FileSystemLoader(TPL), autoescape=True)
    env.filters["thousands"] = lambda v: f"{v:,}"
    env.filters["num"] = lambda v: f"{v:g}"
    html = env.get_template("edition.html.j2").render(**context(doc, e))
    html_path = Path(html_out or Path(out_pdf).with_suffix(".html"))
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.goto(html_path.resolve().as_uri(), wait_until="load")
        over = pg.evaluate("""() => [...document.querySelectorAll('.page')].map((el, i) => {
            const foot = el.querySelector('.foot'); const limit = foot ? foot.offsetTop : el.clientHeight;
            let maxBottom = 0;
            for (const c of el.children) { if (c.classList.contains('foot') || c.classList.contains('sponsor')) continue;
              maxBottom = Math.max(maxBottom, c.offsetTop + c.offsetHeight); }
            const src = el.querySelector('.foot .src');
            return {page: i + 1, over: Math.max(0, maxBottom - limit + 4), srcClipped: src ? src.scrollWidth > src.clientWidth + 1 : false};
        }).filter(x => x.over > 0 || x.srcClipped)""")
        pg.pdf(path=str(out_pdf), format="Letter", print_background=True, prefer_css_page_size=True)
        b.close()
    return over


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--edition", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    doc = json.loads(Path(a.data).read_text())
    e = json.loads(Path(a.edition).read_text())
    errs = check_edition(e, doc["paper"]["date"])
    if errs:
        print("STYLE VIOLATIONS — fix the edition JSON and re-run:\n" + "\n".join(f"- {x}" for x in errs))
        sys.exit(2)
    if a.check_only:
        print("edition words pass")
        return
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    over = render(doc, e, a.out)
    if over:
        print("LAYOUT OVERFLOW — shorten the slot on the page named:\n" + "\n".join(map(str, over)))
        sys.exit(3)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
