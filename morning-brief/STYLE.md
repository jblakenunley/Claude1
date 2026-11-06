# Morning Brief — style guide

Four pages, every day, same layout. Page 1 is snow and roads: Aspen's mountains first, then all of Colorado. Pages 2 and 3 are the news, a free substitute for the FT and the New York Times. Page 4 is free events. The template is locked. Only the words and numbers change, and `render.py` refuses an edition that breaks this page.

## Voice
- **Plain verdicts.** Say what is happening and what it means for a skier or driver. "Dry through Thursday." Not "guidance suggests a drier pattern may develop."
- **Name a source only when the forecast is the news.** "NWS has a Winter Weather Advisory…" is right. "Per the mirror…" is never right.
- **No parentheticals.** No brackets, footnotes, "est.", "stale", "unconfirmed" or "per the". If a fact needs a caveat to be true, leave the fact out.
- **Omit missing data.** No "—", "n/a", "data unavailable" or apology. The template drops the empty cell, row, column or tile on its own.
- **Never invent a number.** Page 1 figures come from the data file; the words restate it or NWS's own wording.
- **Direct, specific, senior.** Never write "leverage", "synergy", "unlock", "in today's landscape" or "it's important to note".

## Numbers
- US units only: inches, °F, feet, mph. No cm, mm, °C, km, hPa or mb anywhere.
- Snow depth in whole inches. Water to one decimal. Percent of median as a whole number.
- NWS snow comes in NWS's bands: "2 to 4 inches" in prose and "2–4 in" in tables. Never add bands together.
- Markets: indexes to the point, yields to two decimals with the change in basis points, commodities in dollars and the euro to four decimals. Each cell shows the day it is for.

## Sources
One footer line on page 1, built from the data file. Story and event links sit on the items themselves. Provenance, fetch logs, forecast scores, fact-check counts, source health and data gaps go to the archive record, never the paper. The CDOT notice prints as fine print whenever COtrip data is used, because CDOT's feed terms require it.

## Slots
| Slot | Limit |
|---|---|
| Headline | 4–12 words. The single most useful snow or road fact. |
| Verdict | 12–40 words. What the next 48 hours bring and where to ski. |
| Day in brief | 20–40 words. The two things a reader must know today. |
| Lead story | Head 4–12 words, text 35–60 words, one or two free links. |
| Every story | Lead 1–5 words, text 8–24 words, one or two free links. |
| Page 2 | Markets 2–3, World 3–4, US & politics 3–4, Economy & central banks 2–3, Europe & UK 2–3. |
| Page 3, weekdays | Companies 3–4, Financials & market structure 2–3, Tech & AI 3–4, Asia-Pacific 2–3, Middle East & energy 2–3, Science, health & climate 1–2; the week ahead in 3–6 lines; one long read. |
| Page 3, weekends | Week in review 4–6, Opinion & ideas 2–3, Long reads 2–3, Arts & books 2–3, Travel, food & living 1–2, Business & tech weekend 2–3. |
| Pick of the week | Title up to 10 words, why up to 18, plus when and where. |
| Events | Up to 18, sorted by time within each day. Title up to 8 words, place up to 6, labelled FREE or NO FEE LISTED, with RSVP when needed. Up to 3 ongoing exhibitions and 3 coming-up events. |
| Sponsor | Optional, up to 6 words, top right. |
| Resort status | Optional, up to 4 words per resort, only from the resort's own page. |

## Choosing
- **Headline order:** an NWS watch, warning or advisory for the Aspen area; then a storm total; then Aspen Snowmass or Independence Pass news; then the dry or wet outlook.
- **News:** cover the day the way the FT and the Times would, and fill each section toward its maximum. Rank by what moves markets, policy or people's lives; include one market-structure item when there is one. Use the last 24 hours, 72 on Mondays, and 7 days for science and long reads. Use free links only; the renderer rejects FT, NYT, WSJ, Bloomberg, The Economist and other paywalled hosts. Never repeat a story from the last three editions unless it has moved on, and never cover one story in two sections.
- **Events:** free to walk into within the next seven days. Pitkin County and Basalt from any good source; Carbondale and Glenwood Springs only when a local paper lists them. Adults first. Fold routine kids' programs into one row.

## Look
Bauhaus: red, yellow, blue and black on warm paper, Inter and Inter Display, lowercase heads, heavy rules, no photos or gradients. A blue circle means GO, a yellow triangle CAUTION and a red square NO-GO. The masthead shapes rotate by issue number. The template and CSS are locked; only the words change.
