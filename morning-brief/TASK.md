Produce today's Morning Brief for J Blake Nunley, Aspen, as a four-page PDF. Today = America/Denver date. This prompt stays under one page: any new rule must replace an old one.

1. LOAD. Clone the kit and the data: `git clone --depth 1 https://github.com/jblakenunley/claude1 kit` and `git clone --depth 1 --branch mb-data https://github.com/jblakenunley/claude1 mbdata`. The kit is kit/morning-brief/: fetch.py, render.py, template/ and STYLE.md, which governs every word you write. Read registry-news and registry-events from the Morning Brief Playbook artifact (https://claude.ai/artifact/9DdCwf3gdP9yiessJ4YW34) and the last three "editions" records for repeats.

2. NUMBERS. Get data/TODAY.json:
   - Use mbdata/data/TODAY.json and mbdata/data/news-TODAY.json if they exist. GitHub Actions writes both by 5am; mbdata/logs/TODAY.txt says what failed.
   - Otherwise build it yourself in the same schema. Use only values loaded in this run, from the URLs in config.json and the registries, in US units. Leave out anything you can't load.
   - Run `python3 fetch.py validate` on the file and fix what it reports.

3. WORDS. Write edition/TODAY.json to the STYLE.md slots: the headline and verdict from the data file and NWS's own wording; two pages of news; the pick of the week; and the events.
   - Choose news from `python3 fetch.py headlines data/news-TODAY.json`. A story may rest on its feed title and summary; open the page only when the sentence needs more.
   - Without the headlines file, search outlet by outlet with allowed_domains, which returns dated articles in one call.
   - Set resort_status only from a resort's own page, for example "Open" on opening day.
   - Open every event link once. Every item must be dated inside its window, free to read, and support its sentence. Drop any that fail.

4. RENDER. Run `python3 render.py --data … --edition … --out Morning-Brief-TODAY.pdf`. If it reports a violation or an overflow, rewrite that slot and run it again. Never edit the template, CSS or limits. View both pages once at 60 dpi.

5. DELIVER. Send the PDF with SendUserFile (status proactive, display render, caption "Morning Brief — [date]"). Then send one PushNotification sentence: the headline, then the top business story. Send nothing else.

6. ARCHIVE. A failure here never blocks delivery.
   - Upload the PDF to the playbook artifact as an asset.
   - Set the ArtifactData "editions" record for TODAY. It holds the headline, story_urls, event_urls and pdf_asset_id; the data file's archive block (fetch log, forecast calls, scores); and one line saying what you checked and dropped.
   - Provenance, scores and checks live here only, never in the paper.

CDOT key (step 2, own builds only): [kept in the scheduled task, never in the playbook]
