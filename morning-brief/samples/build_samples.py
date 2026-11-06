"""Builds the sample data and edition files for 4, 5 and 6 Nov 2026 from what the old Morning Brief runs
archived (ArtifactData records and the 6 Nov Drive text edition). Every number here was in those records;
anything they did not hold is left out, which is how the paper handles missing data."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
(OUT / "data").mkdir(exist_ok=True)
(OUT / "edition").mkdir(exist_ok=True)

ASPEN = [(542, "Independence Pass"), (737, "Schofield Pass"), (618, "McClure Pass"), (669, "North Lost Trail"),
         (556, "Kiln"), (547, "Ivanhoe"), (369, "Brumley")]


def stations(swe, depth=None, pct=None, d24=None):
    out = []
    for sid, name in ASPEN:
        s = {"id": sid, "name": name, "swe_in": swe.get(name)}
        if depth:
            s["depth_in"] = depth.get(name)
        if pct and name in pct:
            s["pct_median"] = pct[name]
        if d24:
            s["depth_24h_in"] = d24.get(name)
        out.append(s)
    return out


def resorts(day):
    opens = lambda d: "Opens today" if d == day else f"Opens {int(d[8:])} Nov" if d[5:7] == "11" else f"Opens {int(d[8:])} Dec"
    summit = [{"name": "Breckenridge", "status": opens("2026-11-06")}, {"name": "Copper", "status": opens("2026-11-06")}]
    if day >= "2026-11-05":  # the archived OpenSnow report lists Keystone and A-Basin open from 5 Nov
        summit = [{"name": "Arapahoe Basin", "status": "Open"}, {"name": "Keystone", "status": "Open"}] + summit
    return {
        "Roaring Fork": [{"name": "Aspen Mountain", "status": opens("2026-11-26")}, {"name": "Aspen Highlands", "status": opens("2026-12-12")},
                         {"name": "Snowmass", "status": opens("2026-11-26")}, {"name": "Buttermilk", "status": opens("2026-12-12")}],
        "Elk & Gunnison": [{"name": "Crested Butte", "status": opens("2026-11-25")}],
        "Sawatch": [{"name": "Ski Cooper", "status": opens("2026-12-09")}],
        "Vail Valley": [{"name": "Vail", "status": opens("2026-11-13")}, {"name": "Beaver Creek", "status": opens("2026-11-25")}],
        "Summit & I-70": summit,
        "Northern": [{"name": "Eldora", "status": opens("2026-11-13")}],
        "Southwest": [{"name": "Purgatory", "status": opens("2026-11-20")}, {"name": "Silverton", "status": opens("2026-12-31")}],
    }


def regions(day, home_extra, avy):
    rs = resorts(day)
    out = []
    for name in rs:
        r = {"name": name, "home": name == "Roaring Fork", "resorts": rs[name]}
        if name == "Roaring Fork":
            r.update(home_extra)
        if avy.get(name):
            r["avalanche"] = avy[name]
        out.append(r)
    return out


ALL_LOW = {k: "Low" for k in ["Roaring Fork", "Elk & Gunnison", "Sawatch", "Vail Valley", "Summit & I-70", "Northern", "Southwest"]}

DAYS = {}

# ------------------------------------------------------------------ Friday 6 Nov 2026, Nº 040
DAYS["2026-11-06"] = (
    {"date": "2026-11-06", "issue": "040", "weekday": "Friday",
     "snow": {"stations": stations(
         {"Brumley": 2.2, "Independence Pass": 2.4, "Ivanhoe": 2.1, "Kiln": 1.5, "McClure Pass": 1.3, "North Lost Trail": 1.2, "Schofield Pass": 4.1},
         {"Brumley": 14, "Independence Pass": 11, "Ivanhoe": 12, "Kiln": 9, "McClure Pass": 4, "North Lost Trail": 5, "Schofield Pass": 16},
         {"Independence Pass": 126, "Schofield Pass": 146, "Brumley": 275},
         {"Brumley": -3, "Independence Pass": -2, "Ivanhoe": -2, "Kiln": -2, "McClure Pass": -4, "North Lost Trail": -3, "Schofield Pass": -2}),
         "median_depth_in": 11, "median_swe_in": 2.1, "new_24h_in": 0, "indep_swe_in": 2.4, "indep_pct_median": 126},
     "summit": {"name": "Aspen Mountain summit", "elev_ft": 10850,
                "next48h": {"text": "none", "low_in": 0, "high_in": 0, "when": None, "label": "NWS zone forecast for Aspen"}},
     "regions": regions("2026-11-06", {"pct_median": 146, "new_24h_in": 0, "next48h": "none"}, ALL_LOW),
     "roads": [
         {"route": "Aspen to Snowmass", "verdict": "CAUTION", "reason": "Road surface 32°F at Brush Creek, slick spots early"},
         {"route": "Independence Pass", "verdict": "NO-GO", "reason": "Closed MP 51.4 to 68.5"},
         {"route": "To Denver via Glenwood and I-70", "verdict": "CAUTION", "reason": "Open and dry; road surface 26°F at Copper"},
         {"route": "To Vail", "verdict": "GO", "reason": "Glenwood Canyon and I-70 open and dry"},
         {"route": "Red Mountain Pass", "verdict": "GO", "reason": "Open and dry"},
         {"route": "Wolf Creek Pass", "verdict": "NO-GO", "reason": "Closed MP 157 to 184.5"}],
     "markets": [
         {"name": "S&P 500", "value": 7353.73, "change_pct": -4.4, "as_of": "2026-11-05", "fmt": "index"},
         {"name": "Dow", "value": 51523.06, "change_pct": -3.4, "as_of": "2026-11-05", "fmt": "index"},
         {"name": "Nasdaq", "value": 24315, "change_pct": -5.5, "as_of": "2026-11-05", "fmt": "index"},
         {"name": "US 10-yr", "value": 4.835, "as_of": "2026-11-06", "fmt": "yield"},
         {"name": "Brent", "value": 99.90, "change_pct": 1.6, "as_of": "2026-11-06", "fmt": "usd"},
         {"name": "Gold", "value": 4047, "as_of": "2026-11-06", "fmt": "usd"}],
     "sources": ["NRCS SNOTEL 6 Nov", "NWS Grand Junction 6 Nov 3:38am", "avalanche.org", "COtrip and CDOT 6 Nov 5:33am",
                 "OpenSnow", "AP", "Trading Economics"],
     "cdot_notice": True},
    {"headline": "Dry into next week after the midweek storm's 8 inches",
     "verdict": "No snow in the NWS forecast for the Aspen area through Thursday, with highs in the mid-40s to mid-50s from Sunday. "
                "Keystone and A-Basin are open; Breckenridge and Copper plan to open today.",
     "business": [
         {"lead": "Worst day since April 2025", "text": "The S&P 500 fell 4.4% and the Nasdaq Composite 5.5% on Thursday as investors dumped AI and chip stocks on fears a Democratic Congress slows data-centre buildouts.",
          "outlet": "AP via Yahoo", "url": "https://ca.finance.yahoo.com/news/major-us-stock-indexes-fared-212218583.html"},
         {"lead": "Asia's chip stocks crack", "text": "The Nikkei fell as much as 7% and Korea's Kospi dropped 8.8%, tripping a 20-minute halt; SK Hynix lost about 10% and TSMC up to 8.5%.",
          "outlet": "Euronews", "url": "https://www.euronews.com/2026/11/06/global-stock-rout-deepens-as-ai-data-centre-fears-fuel-worst-us-chip-sell-off-since-2020"},
         {"lead": "Meta names the political risk", "text": "Meta's president said the Democratic wins will make data centres harder to build and expects more project reviews, the risk markets are now pricing.",
          "outlet": "TechCrunch", "url": "https://techcrunch.com/2026/11/05/metas-warns-that-election-backlash-against-data-centers-could-make-ai-expansion-harder/"},
         {"lead": "Tokenised equity trades print", "text": "The first equity trades under the SEC's Innovation Exemption printed on Wednesday, with DRW Cumberland buying tokenised Canton Strategic Holdings stock on the permissioned TSV venue.",
          "outlet": "Markets Media", "url": "https://www.marketsmedia.com/first-equity-trades-executed-under-sec-innovation-exemption/"},
         {"lead": "Iran keeps oil near $100", "text": "Trump said the US may have to destroy the rest of Iran, while Tehran reportedly sent a nuclear proposal through Qatar with seven demands attached.",
          "outlet": "Al Jazeera", "url": "https://www.aljazeera.com/news/liveblog/2026/11/6/iran-war-live-trump-warns-us-may-have-to-destroy-rest-of-iran"}],
     "next": "October payrolls at 6:30am MT today, consensus +65K. CPI on Tuesday 10 Nov, PPI on Friday 13 Nov.",
     "pick": {"title": "Pam Houston on Animals Taught Me Everything", "why": "A live podcast recording with Mitzi Rapkin, then questions and a signing.",
              "when": "Wed 11 Nov, 6:30pm", "place": "Pitkin County Library, Aspen",
              "url": "https://pitcolib.org/library-events/animals-taught-me-everything-conversation-author-pam-houston-mitzi-rapkin-podcast"},
     "events": [
         {"day": "Fri 6", "time": "5–7pm", "title": "Chris Hassig and Rachel Becker openings", "place": "The Art Base, Basalt", "kind": "art", "label": "FREE",
          "url": "https://www.aspenpublicradio.org/community-calendar/event/chris-hassig-19-01-2026-11-21-41"},
         {"day": "Fri 6", "time": "5–8pm", "title": "First Friday Día de los Muertos", "place": "Main Street, Carbondale", "kind": "com", "label": "FREE",
          "url": "https://www.aspenpublicradio.org/community-calendar/event/first-friday-dia-de-los-muertos-celebration-23-09-2026-09-03-24"},
         {"day": "Sat 7", "time": "11:30am", "title": "Persistence and Grit, a talk", "place": "Glenwood Library, Glenwood Springs", "kind": "art", "label": "NO FEE LISTED",
          "url": "https://soprissun.com/calendar-nov-5-15-2026/"},
         {"day": "Sun 8", "time": "2pm", "title": "Museum tour in Spanish", "place": "Aspen Art Museum, Aspen", "kind": "art", "label": "FREE",
          "url": "https://aspenartmuseum.org/event/recorridos-por-el-museo-en-espanol-november-8/"},
         {"day": "Sun 8", "time": "3–6pm", "title": "Día de los Muertos celebration", "place": "Aspen Art Museum, Aspen", "kind": "com", "label": "FREE", "rsvp": True,
          "url": "https://aspenartmuseum.org/event/arte-en-espanol-2026-dia-de-los-muertos-celebration/"},
         {"day": "Mon 9", "time": "5:30pm", "title": "Nonfiction Book Club: The Havana Syndrome", "place": "Pitkin County Library, Aspen", "kind": "art", "label": "NO FEE LISTED",
          "url": "https://pitcolib.org/nonfiction-book-club/book-of-the-month/nonfiction-book-club-havana-syndrome-secret-weapons"},
         {"day": "Tue 10", "time": "4:30pm", "title": "Steven Yazzie, visiting-artist lecture", "place": "Anderson Ranch, Snowmass Village", "kind": "art", "label": "FREE",
          "url": "https://www.aspenpublicradio.org/community-calendar/event/steven-yazzie-visiting-artist-lecture-24-09-2026-17-45-45"},
         {"day": "Tue 10", "time": "6pm", "title": "From Page to Stage poetry showcase", "place": "Crystal Theatre, Carbondale", "kind": "art", "label": "FREE", "rsvp": True,
          "url": "https://www.aspenpublicradio.org/community-calendar/event/from-page-to-stage-aspen-words-poetry-showcase-20-10-2026-15-25-41"},
         {"day": "Wed 11", "time": "5:30pm", "title": "Logan Phillips reads from Reckon", "place": "Explore Books, Aspen", "kind": "art", "label": "FREE",
          "url": "https://www.aspenpublicradio.org/community-calendar/event/logan-phillips-at-explore-books-16-10-2026-11-34-58"},
         {"day": "Wed 11", "time": "6:30pm", "title": "Pam Houston and Mitzi Rapkin", "place": "Pitkin County Library, Aspen", "kind": "art", "label": "NO FEE LISTED",
          "url": "https://pitcolib.org/library-events/animals-taught-me-everything-conversation-author-pam-houston-mitzi-rapkin-podcast"},
         {"day": "Thu 12", "time": "10am", "title": "Community Mahjong Club", "place": "Pitkin County Library, Aspen", "kind": "com", "label": "FREE",
          "url": "https://pitcolib.org/library-events/community-mahjong-club-1112261000"}]})

# ------------------------------------------------------------------ Thursday 5 Nov 2026, Nº 039
DAYS["2026-11-05"] = (
    {"date": "2026-11-05", "issue": "039", "weekday": "Thursday",
     "snow": {"stations": stations(
         {"Brumley": 2.3, "Independence Pass": 2.5, "Ivanhoe": 2.1, "Kiln": 1.5, "McClure Pass": 1.3, "North Lost Trail": 1.2, "Schofield Pass": 4.1},
         {"Brumley": 17, "Independence Pass": 13, "Ivanhoe": 14, "Kiln": 11, "McClure Pass": 8, "North Lost Trail": 8, "Schofield Pass": 18}),
         "median_depth_in": 13, "new_24h_in": 8, "indep_swe_in": 2.5},
     "summit": {"name": "Aspen Mountain summit", "elev_ft": 10850,
                "next48h": {"text": "none", "low_in": 0, "high_in": 0, "when": None, "label": "NWS zone forecast for Aspen"}},
     "regions": regions("2026-11-05", {"next48h": "none"}, {"Roaring Fork": "Moderate"}),
     "roads": [
         {"route": "Aspen to Snowmass", "verdict": "GO", "reason": "No incidents; air 30°F at Snowmass Creek"},
         {"route": "Independence Pass", "verdict": "NO-GO", "reason": "Closed MP 51.4 to 68.5"},
         {"route": "To Denver via Glenwood and I-70", "verdict": "CAUTION", "reason": "Snow and ice on I-70; black ice on Vail Pass"},
         {"route": "To Vail", "verdict": "CAUTION", "reason": "Black ice on Vail Pass, 16°F"},
         {"route": "Red Mountain Pass", "verdict": "CAUTION", "reason": "Wet, 27°F; traction law"},
         {"route": "Wolf Creek Pass", "verdict": "NO-GO", "reason": "Closed MP 157 to 184.5"}],
     "markets": [
         {"name": "Dow", "value": 53599.97, "change_pct": 3.0, "as_of": "2026-11-04", "fmt": "index"},
         {"name": "US 10-yr", "value": 4.847, "as_of": "2026-11-05", "fmt": "yield"},
         {"name": "Brent", "value": 95.86, "change_pct": -6.8, "as_of": "2026-11-05", "fmt": "usd"}],
     "sources": ["NRCS SNOTEL 5 Nov", "NWS Grand Junction 5 Nov 5:13am", "OpenSnow", "COtrip and CDOT 5 Nov 4:03am", "Trading Economics"],
     "cdot_notice": True},
    {"headline": "Midweek storm leaves 8 inches; dry through Veterans Day",
     "verdict": "The seven Aspen-area sites gained a median 8 inches of snow overnight, about an inch of water. "
                "NWS cancelled the advisory at 2:56am and keeps the Aspen zone dry through Veterans Day.",
     "business": [
         {"lead": "Bank of England hikes to 4%", "text": "The BoE raised Bank Rate a quarter point to 4.00% this morning on a 9 to 0 vote.",
          "outlet": "investingLive", "url": "https://investinglive.com/central-banks/bank-of-england-raises-the-bank-rate-to-4-00-as-expected-in-a-9-0-vote"},
         {"lead": "Dow's best day since April 2025", "text": "The Dow jumped 1,569 points, or 3.03%, to about 53,600 on Wednesday after the midterms; tech futures are falling again this morning.",
          "outlet": "ABC News", "url": "https://abcnews.com/Business/dow-surges-1000-points-democrats-control-congress/story?id=137842989"},
         {"lead": "Oil slides on war-exit bets", "text": "Brent fell below $96 after Vice President Vance blamed the Iran war for the Republicans' midterm losses.",
          "outlet": "investingLive", "url": "https://investinglive.com/commodities/oil-prices-tumble-as-republicans-midterm-loss-sparks-bets-on-iran-war-exit-trump-still-has-the-final-say/"},
         {"lead": "Canva cuts 22% of staff", "text": "Canva is laying off 1,271 people, about 22% of its workforce, as growth slows.",
          "outlet": "TechCrunch", "url": "https://techcrunch.com/2026/11/04/canva-lays-off-over-1200-people-amid-slowing-growth/"},
         {"lead": "CME sets an October record", "text": "CME Group reported record October average daily volume of 30 million contracts.",
          "outlet": "Markets Media", "url": "https://www.marketsmedia.com/cme-group-reports-record-october-adv/"}],
     "next": "October payrolls on Friday at 6:30am MT. CPI on Tuesday 10 Nov, PPI on Friday 13 Nov.",
     "pick": {"title": "From Page to Stage", "why": "An Aspen Words poetry showcase, free with registration.",
              "when": "Tue 10 Nov, 6pm", "place": "Crystal Theatre, Carbondale",
              "url": "https://www.aspenpublicradio.org/community-calendar/event/from-page-to-stage-aspen-words-poetry-showcase-20-10-2026-15-25-41"},
     "events": [
         {"day": "Thu 5", "time": "10am", "title": "Community Mahjong Club", "place": "Pitkin County Library, Aspen", "kind": "com", "label": "FREE",
          "url": "https://pitcolib.org/library-events/community-mahjong-club-1105261000"},
         {"day": "Thu 5", "time": "12:30pm", "title": "Colorado Mountain College open hours", "place": "Pitkin County Library, Aspen", "kind": "art", "label": "NO FEE LISTED",
          "url": "https://pitcolib.org/library-events/colorado-mountain-college-open-hours-1105261230"},
         {"day": "Thu 5", "title": "Valle Musico in concert", "place": "Basalt Library, Basalt", "kind": "art", "label": "NO FEE LISTED",
          "url": "https://business.basaltchamber.org/events/details/music-at-the-library-valle-musico-in-concert-37966"},
         {"day": "Fri 6", "time": "5–7pm", "title": "Chris Hassig and Rachel Becker openings", "place": "The Art Base, Basalt", "kind": "art", "label": "FREE",
          "url": "https://www.aspenpublicradio.org/community-calendar/event/chris-hassig-19-01-2026-11-21-41"},
         {"day": "Fri 6", "time": "5–8pm", "title": "First Friday Día de los Muertos", "place": "Main Street, Carbondale", "kind": "com", "label": "FREE",
          "url": "https://www.aspenpublicradio.org/community-calendar/event/first-friday-dia-de-los-muertos-celebration-23-09-2026-09-03-24"},
         {"day": "Sat 7", "time": "3:30pm", "title": "Dungeons and Dragons for teens", "place": "Pitkin County Library, Aspen", "kind": "fam", "label": "NO FEE LISTED",
          "url": "https://pitcolib.org/library-events/dungeons-dragons-1107261530"},
         {"day": "Sun 8", "time": "2pm", "title": "Museum tour in Spanish", "place": "Aspen Art Museum, Aspen", "kind": "art", "label": "FREE",
          "url": "https://aspenartmuseum.org/event/recorridos-por-el-museo-en-espanol-november-8/"},
         {"day": "Sun 8", "time": "3–6pm", "title": "Día de los Muertos celebration", "place": "Aspen Art Museum, Aspen", "kind": "com", "label": "FREE", "rsvp": True,
          "url": "https://aspenartmuseum.org/event/arte-en-espanol-2026-dia-de-los-muertos-celebration/"},
         {"day": "Mon 9", "time": "5:30pm", "title": "Nonfiction Book Club: The Havana Syndrome", "place": "Pitkin County Library, Aspen", "kind": "art", "label": "NO FEE LISTED",
          "url": "https://pitcolib.org/nonfiction-book-club/book-of-the-month/nonfiction-book-club-havana-syndrome-secret-weapons"},
         {"day": "Tue 10", "time": "4:30pm", "title": "Steven Yazzie, visiting-artist lecture", "place": "Anderson Ranch, Snowmass Village", "kind": "art", "label": "FREE",
          "url": "https://www.aspenpublicradio.org/community-calendar/event/steven-yazzie-visiting-artist-lecture-24-09-2026-17-45-45"},
         {"day": "Tue 10", "time": "6pm", "title": "From Page to Stage poetry showcase", "place": "Crystal Theatre, Carbondale", "kind": "art", "label": "FREE", "rsvp": True,
          "url": "https://www.aspenpublicradio.org/community-calendar/event/from-page-to-stage-aspen-words-poetry-showcase-20-10-2026-15-25-41"},
         {"day": "Wed 11", "time": "5:30pm", "title": "Logan Phillips reads from Reckon", "place": "Explore Books, Aspen", "kind": "art", "label": "FREE",
          "url": "https://www.aspenpublicradio.org/community-calendar/event/logan-phillips-at-explore-books-16-10-2026-11-34-58"}]})

# ------------------------------------------------------------------ Wednesday 4 Nov 2026, Nº 038
DAYS["2026-11-04"] = (
    {"date": "2026-11-04", "issue": "038", "weekday": "Wednesday",
     "snow": {"stations": stations(
         {"Brumley": 1.1, "Independence Pass": 1.5, "Ivanhoe": 1.0, "Kiln": 0.6, "McClure Pass": 0.4, "North Lost Trail": 0.4, "Schofield Pass": 3.8},
         pct={"Independence Pass": 94}),
         "indep_swe_in": 1.5, "indep_pct_median": 94},
     "summit": {"name": "Aspen Mountain summit", "elev_ft": 10850,
                "next48h": {"text": "4–8 in", "low_in": 4, "high_in": 8, "when": None, "label": "NWS advisory, above 10,000 ft by Thu 5am"}},
     "alerts": [{"event": "Winter Weather Advisory", "until": "Thu 5am"}],
     "regions": regions("2026-11-04", {"next48h": "4–8 in"}, {"Roaring Fork": "Moderate"}),
     "roads": [
         {"route": "Aspen to Snowmass", "verdict": "GO", "reason": "No incidents; air 24°F at Snowmass Creek"},
         {"route": "Independence Pass", "verdict": "NO-GO", "reason": "Closed MP 51.4 to 68.5"},
         {"route": "To Denver via Glenwood and I-70", "verdict": "CAUTION", "reason": "Open and dry; traction law in effect"},
         {"route": "To Vail", "verdict": "CAUTION", "reason": "Traction law; Vail Pass 22°F"},
         {"route": "Red Mountain Pass", "verdict": "CAUTION", "reason": "Open and dry; traction law in effect"},
         {"route": "Wolf Creek Pass", "verdict": "NO-GO", "reason": "Closed MP 157 to 184.5"}],
     "markets": [
         {"name": "Dow", "value": 51786, "change_pct": -0.4, "as_of": "2026-11-03", "fmt": "index"},
         {"name": "US 10-yr", "value": 4.944, "as_of": "2026-11-04", "fmt": "yield"},
         {"name": "Brent", "value": 102.84, "change_pct": -0.7, "as_of": "2026-11-04", "fmt": "usd"},
         {"name": "Gold", "value": 4043, "change_pct": 2.8, "as_of": "2026-11-04", "fmt": "usd"}],
     "sources": ["NRCS SNOTEL 4 Nov", "NWS Grand Junction 4 Nov 3:23am", "OpenSnow", "COtrip and CDOT 4 Nov 2:48am", "SRN News", "Trading Economics"],
     "cdot_notice": True},
    {"headline": "Advisory: 4 to 8 inches above 10,000 feet by Thursday",
     "verdict": "NWS has a Winter Weather Advisory for the Gore and Elk Mountains from 2pm today to 5am Thursday. "
                "The zone forecast calls for about an inch today and 2 to 4 inches tonight.",
     "business": [
         {"lead": "Democrats take Congress", "text": "Democrats won control of the House and Senate in Tuesday's midterms, flipping seven Senate seats.",
          "outlet": "CBS News", "url": "https://www.cbsnews.com/live-updates/election-day-2026-midterms/"},
         {"lead": "Futures slide, then recover", "text": "Nasdaq futures fell more than 2% overnight before paring losses, while AMD and Arista posted strong quarters.",
          "outlet": "investingLive", "url": "https://investinglive.com/stocks/nasdaq-futures-slide-after-trump-s-midterm-setback-amd-and-arista-are-telling-a-different-story/"},
         {"lead": "CrowdStrike buys AI security", "text": "CrowdStrike will pay nearly $500 million for two AI security startups as demand for securing AI agents grows.",
          "outlet": "TechCrunch", "url": "https://techcrunch.com/2026/11/03/crowdstrike-to-shell-out-nearly-500m-for-2-ai-security-startups-as-the-market-for-securing-agents-takes-off/"},
         {"lead": "UK nears a digital gilt", "text": "The UK moved closer to issuing its first digitally native gilt, with a pilot targeted by early 2027.",
          "outlet": "Markets Media", "url": "https://www.marketsmedia.com/uk-moves-closer-to-issuing-first-digitally-native-gilt/"},
         {"lead": "Equity perpetuals arrive", "text": "US perpetual futures are extending to individual equities on CFTC-regulated exchanges.",
          "outlet": "Markets Media", "url": "https://www.marketsmedia.com/u-s-perpetual-futures-extend-to-individual-equities/"}],
     "next": "Bank of England decides on Thursday, with a hike to 4.00% expected.",
     "pick": {"title": "Steven Yazzie, visiting-artist lecture", "why": "A free public lecture by a visiting artist.",
              "when": "Tue 10 Nov, 4:30pm", "place": "Anderson Ranch, Snowmass Village",
              "url": "https://www.aspenpublicradio.org/community-calendar/event/steven-yazzie-visiting-artist-lecture-24-09-2026-17-45-45"},
     "events": [
         {"day": "Wed 4", "title": "Books and Brews Book Club", "place": "Aspen Brewing Co, Aspen", "kind": "art", "label": "NO FEE LISTED",
          "url": "https://pitcolib.org/books-brews-book-club/book-of-the-month/books-brews-book-club-bat-eater-and-other-names-cora-zeng"},
         {"day": "Thu 5", "time": "10am", "title": "Community Mahjong Club", "place": "Pitkin County Library, Aspen", "kind": "com", "label": "FREE",
          "url": "https://pitcolib.org/library-events/community-mahjong-club-1105261000"},
         {"day": "Thu 5", "title": "Valle Musico in concert", "place": "Basalt Library, Basalt", "kind": "art", "label": "NO FEE LISTED",
          "url": "https://business.basaltchamber.org/events/details/music-at-the-library-valle-musico-in-concert-37966"},
         {"day": "Thu 5", "title": "Snowmass Village Book Club", "place": "Snowmass Village", "kind": "art", "label": "NO FEE LISTED",
          "url": "https://pitcolib.org/snowmass-village-book-club/book-of-the-month/snowmass-village-book-club-boy-swallows-universe"},
         {"day": "Fri 6", "time": "5–7pm", "title": "Chris Hassig and Rachel Becker openings", "place": "The Art Base, Basalt", "kind": "art", "label": "FREE",
          "url": "https://www.aspenpublicradio.org/community-calendar/event/chris-hassig-19-01-2026-11-21-41"},
         {"day": "Fri 6", "time": "5–8pm", "title": "First Friday Día de los Muertos", "place": "Main Street, Carbondale", "kind": "com", "label": "FREE",
          "url": "https://www.aspenpublicradio.org/community-calendar/event/first-friday-dia-de-los-muertos-celebration-23-09-2026-09-03-24"},
         {"day": "Sat 7", "time": "3:30pm", "title": "Dungeons and Dragons for teens", "place": "Pitkin County Library, Aspen", "kind": "fam", "label": "NO FEE LISTED",
          "url": "https://pitcolib.org/library-events/dungeons-dragons-1107261530"},
         {"day": "Sun 8", "time": "2pm", "title": "Museum tour in Spanish", "place": "Aspen Art Museum, Aspen", "kind": "art", "label": "FREE",
          "url": "https://aspenartmuseum.org/event/recorridos-por-el-museo-en-espanol-november-8/"},
         {"day": "Sun 8", "time": "3–6pm", "title": "Día de los Muertos celebration", "place": "Aspen Art Museum, Aspen", "kind": "com", "label": "FREE", "rsvp": True,
          "url": "https://aspenartmuseum.org/event/arte-en-espanol-2026-dia-de-los-muertos-celebration/"},
         {"day": "Mon 9", "time": "5:30pm", "title": "Nonfiction Book Club: The Havana Syndrome", "place": "Pitkin County Library, Aspen", "kind": "art", "label": "NO FEE LISTED",
          "url": "https://pitcolib.org/nonfiction-book-club/book-of-the-month/nonfiction-book-club-havana-syndrome-secret-weapons"},
         {"day": "Tue 10", "time": "1pm", "title": "Let's Chat in Spanish", "place": "Pitkin County Library, Aspen", "kind": "com", "label": "NO FEE LISTED",
          "url": "https://pitcolib.org/library-events/lets-chat-spanish-conversemos-en-espanol-1110261300"},
         {"day": "Tue 10", "time": "4:30pm", "title": "Steven Yazzie, visiting-artist lecture", "place": "Anderson Ranch, Snowmass Village", "kind": "art", "label": "FREE",
          "url": "https://www.aspenpublicradio.org/community-calendar/event/steven-yazzie-visiting-artist-lecture-24-09-2026-17-45-45"}]})

for day, (paper, _old_business_words) in DAYS.items():
    (OUT / "data" / f"{day}.json").write_text(json.dumps({"schema": 2, "paper": paper, "archive": {"note": "sample built from archived records"}}, indent=1, ensure_ascii=False))
print("built data for", ", ".join(DAYS), "; the 6 Nov edition words live in edition/2026-11-06.json")
