"""Fills every slot to its word and item maximum and renders, so the locked layout is proven to hold the
fullest possible edition. Run after any template or limit change: python3 tests/capacity.py"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import render

W = ("The Nikkei fell as much as 7% and Korea's Kospi dropped 8.8%, tripping a 20-minute halt; SK Hynix lost about 10% "
     "and TSMC up to 8.5% as the rout spread across the region on Friday.").split()  # real copy, typical word length
def txt(n): return " ".join((W * 4)[:n])
def item(): return {"lead": txt(5), "text": txt(24), "outlet": "Al Jazeera", "url": "https://example.org/a"}

def edition(kind):
    secs = {k: [item() for _ in range(hi)] for k, _, (lo, hi) in render.PAGE2 + render.PAGE3[kind]}
    ev = [{"day": f"Day {i // 3}", "time": "5:30pm", "title": txt(8), "place": txt(6), "kind": "art", "label": "FREE",
           "rsvp": True, "url": "https://example.org/e"} for i in range(18)]
    return {"headline": txt(12), "verdict": txt(32), "brief": txt(40), "sponsor": txt(6),
            "lead": {"head": txt(12), "text": txt(60), "outlet": "AP via Yahoo", "url": "https://example.org/l",
                     "outlet2": "Euronews", "url2": "https://example.org/l2"},
            "sections": secs, "week": [{"day": "Wed 11", "text": txt(16)} for _ in range(6)],
            "longread": {"title": txt(14), "why": txt(26), "outlet": "Quanta", "minutes": 25, "url": "https://example.org/r"},
            "pick": {"title": txt(10), "why": txt(18), "when": "Wed 11 Nov, 6:30pm", "place": txt(6), "url": "https://example.org/p"},
            "events": ev, "ongoing": [{"title": txt(8), "place": txt(6), "until": "31 Mar 2027", "url": "https://example.org/o"}] * 3,
            "coming": [{"title": txt(8), "when": "Wed 18 Nov, 5:30pm", "place": txt(6), "url": "https://example.org/c"}] * 3}

doc = json.loads((HERE / "samples/data/2026-11-06.json").read_text())
doc["paper"]["markets"] = [{"name": n, "value": 51523.06, "change_pct": -3.4, "as_of": "2026-11-05", "fmt": "index"}
                           for n in ["S&P 500", "Dow", "Nasdaq", "Stoxx 600", "FTSE 100", "Nikkei", "US 10-yr", "Dollar index", "Euro", "Brent", "Gold", "Bitcoin"]]
cfg = json.loads((HERE / "config.json").read_text())
P = doc["paper"]
P.pop("regions", None)
P["aspen_mountains"] = [{"name": m["name"], "status": "Opens 26 Nov", "next48h": "2–4 in"} for m in cfg["aspen_mountains"]]
P["mountains"] = [{"name": m["name"], "region": m["region"], "status": "Opens 13 Dec", "depth_in": 24, "depth_24h_in": -3,
                   "pct_median": 104, "next48h": "4–8 in", "avalanche": "Considerable"} for m in cfg["mountains"]]
P["roads"] = [{"route": r["name"], "verdict": "NO-GO", "reason": "Closed MP 157 to 184.5"} for r in cfg["routes"]]
P["alerts"] = [{"event": "Winter Storm Warning", "until": "Thu 5am"}, {"event": "Avalanche Warning", "until": "Fri 6pm"}]
P["avalanche_aspen"] = "Considerable"
bad = 0
for kind, day in (("daily", "2026-11-06"), ("weekend", "2026-11-07")):
    doc["paper"]["date"] = day
    e = edition(kind)
    errs = render.check_edition(e, day)
    if errs:
        print(kind, "word-check errors:", errs[:5]); bad += 1
    over = render.render(doc, e, f"/tmp/capacity-{kind}.pdf")
    print(kind, "overflow:", over or "none"); bad += bool(over)
sys.exit(1 if bad else 0)
