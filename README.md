# The Cricket Lens — ESPNcricinfo and Cricbuzz collector

This Python Apify Actor collects ESPNcricinfo RSS and Cricbuzz public news-page metadata. It produces the existing dataset row format, OUTPUT.xlsx and SOURCE_STATUS, so the website success webhook continues to work.

## Update your existing GitHub Actor
1. Replace the files in `amit-webethics/cricket-lens-collector` with the files in this package, including `.actor/`, `src/`, INPUT.json, README.md and tests/.
2. Commit the changes to main. In Apify, rebuild the existing Actor from GitHub.
3. Keep `lookbackHours: 72`; set `maxItemsPerSource` as needed (default 100). Saved BBC/custom `sources` input is intentionally ignored. This version uses only ESPNcricinfo and Cricbuzz.
4. Run a manual trial and inspect SOURCE_STATUS. The existing webhook imports results to the website after a successful run, provided the webhook is already configured.
5. Keep your existing schedule. If creating a new one, twice daily at 09:00 and 18:00 Asia/Kolkata uses `0 9,18 * * *`. This package does not activate or change schedules.

## Source labels and duplicates
Every row includes its publisher name, original headline, source URL, source publication date (when available) and collection time. Excel retains individual source rows for traceability. The website grouping update combines strong matches in the admin and offers manual merge for uncertain coverage; it retains the original records and publisher links.

The Actor deduplicates canonical URLs within each run. Persistent cross-run URL deduplication and cross-source grouping happen in the website, not the workbook. Runs intentionally overlap.

## Scope
- ESPNcricinfo supplies RSS headlines, summaries and tags. Cricbuzz supplies news-listing links and article title, description, section and publication-date metadata where available.
- Only stories linked from the current listing/feed are checked. maxItemsPerSource is an upper bound, not a guaranteed number. No archive/pagination crawling or full article extraction is included.
- Missing dates and future dates are flagged. Source status reports feed failures, parse warnings and partial Cricbuzz article failures. A failure of both publishers fails the Actor run.
- Classification is a suggestion; confirm the section, category, teams and series before publishing. Source metadata cannot guarantee classification accuracy.
- Source summaries are reference material. Write original reporting, verify facts and select images you have permission to use.
- No paywall bypass, AI model call, API key or automatic publication is included in this Actor. The website handles optional section drafting separately.

## Local development
Use Python 3.12. Install `pip install -r requirements.txt`, then run `python -m src.main`. Local SDK input may be placed at `storage/key_value_stores/default/INPUT.json`; otherwise INPUT.json is used.

Run `python -m unittest discover -s tests -v` from this directory. All five tests passed, including Cricbuzz metadata, partial failures, source labels, URL filtering and Excel safety. A workspace smoke test fetched one Cricbuzz story; ESPNcricinfo timed out from this environment. Build and test in Apify before relying on scheduled collection.
