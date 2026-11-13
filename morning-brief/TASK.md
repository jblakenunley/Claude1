Produce today's Morning Brief for J Blake Nunley, Aspen, as a four-page PDF. Today = America/Denver date. This prompt stays under one page: any new rule must replace an old one.

1. LOAD. ToolSearch "select:ArtifactData,PushNotification,SendUserFile" (skip any that don't exist). Clone the kit and the data: `git clone --depth 1 https://github.com/jblakenunley/claude1 kit` and `git clone --depth 1 --branch mb-data https://github.com/jblakenunley/claude1 mbdata`. The kit is kit/morning-brief/: fetch.py, render.py, template/ and STYLE.md, which governs every word you write. Read registry-news and registry-events from the Morning Brief Playbook artifact (https://claude.ai/artifact/9DdCwf3gdP9yiessJ4YW34) and the last three "editions" records for repeats.

2. NUMBERS. Start a fresh fetch, then read it:
   - In kit, run `git commit -q --allow-empty -m "fetch TODAY" && git push -q origin HEAD:refs/heads/mb-trigger-$(date -u +%Y%m%d%H%M)`. This creates a new branch; never force-push. If it is refused, call add_repo for jblakenunley/claude1 with push access and retry once.
   - Poll `git ls-remote origin refs/heads/mb-data` every 20 seconds for up to 4 minutes; when it moves, `git -C mbdata pull`. Use mbdata/data/TODAY.json and mbdata/data/news-TODAY.json; mbdata/logs/TODAY.txt says what failed.
   - If no file for today arrives, build it yourself in the same schema from config.json's URLs and the registries, US units only, leaving out anything you can't load, and run `python3 kit/morning-brief/fetch.py validate` on it.

3. WORDS. Write edition/TODAY.json to the STYLE.md slots: the headline and verdict from the data file and NWS's own wording, printed by `python3 kit/morning-brief/fetch.py nws mbdata/data/TODAY.json`; two pages of news; the pick of the week; and the events.
   - Choose news from `python3 kit/morning-brief/fetch.py headlines mbdata/data/news-TODAY.json`. A story may rest on its feed title and summary; open the page only when the sentence needs more.
   - Without the headlines file, search outlet by outlet with allowed_domains, which returns dated articles in one call.
   - resort_status: carry forward the last edition's; change a resort only from its own page, and check once any resort whose planned opening has passed with no status.
   - Open every event link once. Every item must be dated inside its window, free to read, and support its sentence. Drop any that fail.

4. RENDER. Run `python3 kit/morning-brief/render.py --data mbdata/data/TODAY.json --edition edition/TODAY.json --out Morning-Brief-TODAY.pdf`. If it reports a violation or an overflow, rewrite that slot and run it again. Never edit the template, CSS or limits. View all four pages once at 60 dpi.

5. DELIVER. Send the PDF with SendUserFile (status proactive, display render, caption "Morning Brief — [date]"). Then send one PushNotification sentence: the headline, then the top news story. Send nothing else.

6. ARCHIVE. A failure here never blocks delivery.
   - Upload the PDF with the Artifact tool: action "publish", url the playbook, file_path the PDF, asset true.
   - ArtifactData "set", collection "editions", doc_id TODAY: date, issue, kind, lead (the headline), snow {indep_swe_in, indep_pct_median} from the data file, story_urls, event_urls, resort_status, pdf_asset_id, factcheck {checked, dropped, notes}, and the data file's archive block.
   - Provenance, scores and checks live here only, never in the paper.

CDOT key (step 2, own builds only): [kept in the scheduled task, never in the playbook]
