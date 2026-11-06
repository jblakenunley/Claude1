# Morning Brief

J Blake Nunley's daily paper for Aspen, Colorado: snow and roads, two pages of news, free events.

- `fetch.py` pulls snow, forecast, avalanche, road, lift and market numbers in US units, plus headlines from free news feeds. GitHub Actions runs it every morning (`.github/workflows/morning-brief-data.yml`) and writes the results to the `mb-data` branch.
- `render.py` and `template/` turn those numbers and the day's words into the locked four-page PDF. `tests/capacity.py` proves the fullest edition fits.
- `STYLE.md` governs the words. `TASK.md` is the daily task prompt.

Road data comes from COtrip. The data made available here has been modified for use from its original source, which is the State of Colorado, Department of Transportation (CDOT). THE STATE OF COLORADO AND CDOT MAKES NO REPRESENTATIONS OR WARRANTY AS TO THE COMPLETENESS, ACCURACY, TIMELINESS, OR CONTENT OF ANY DATA MADE AVAILABLE THROUGH THIS SITE. THE STATE OF COLORADO AND CDOT EXPRESSLY DISCLAIMS ALL WARRANTIES, WHETHER EXPRESS OR IMPLIED, INCLUDING ANY IMPLIED WARRANTIES OF MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE. The data is subject to change as modifications and updates are complete. It is understood that the information contained in the Web feed is being used at one's own risk.
