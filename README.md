# The Cricket Lens — Excel Collector v0.1

A Python Apify Actor that collects configured cricket RSS / Atom feeds and produces an editable Excel workbook. No website connection, AI account, or publishing automation is required.

## Run on Apify
1. Create a new custom Actor using a Python template in your Apify account.
2. Replace the template source with this project's files, including `.actor/`, `src/`, Dockerfile and requirements.txt. Alternatively use the Apify CLI from this directory: `apify login`, then `apify push`.
3. Build the Actor. In Input use the supplied sources and a 72-hour lookback for the first trial. `INPUT.json` is a copyable example.
4. Run it. Open the run's Storage / Key-value store and download `OUTPUT.xlsx`. Dataset output also contains story rows.
5. Check the Source status tab, then review and edit the Stories tab. Keep your edited copy separately: each run creates a new workbook.
6. After a successful trial, add an Apify schedule, for example every 4 hours (`0 */4 * * *`) with timezone Asia/Kolkata. Scheduling is not activated by this package.

## Workbook
Stories includes original headline, source link, publication and collection dates, source summary, author, source tags, suggested type, date checks, review status, and blank editorial fields. Source status shows failures explicitly. Instructions explains review steps.

## Scope and limits
- Starts with candidate BBC Cricket and ESPNcricinfo feeds. Live availability must be tested from Apify; sites can change or block feeds. Add further regional, women's and associate cricket feeds to extend coverage.
- Collects only what feeds supply, not full articles or images. Summaries can be empty. No AI-generated summaries or drafts.
- News / preview / opinion / report classification is a headline keyword suggestion and needs review. Teams and series are entered manually in v0.1.
- Deduplicates tracking variants of the same URL within a run. Different sources covering the same event are retained for comparison. Runs intentionally overlap and do not share an exclusion history, so an unsuccessful download cannot silently lose stories.
- Uses published date, falling back to updated date. Undated entries are included and flagged; future dates are flagged. Reads up to maxItemsPerSource feed entries per source. Feed providers determine history depth.
- Source text is retained as reference, not a publish-ready article. Review source access/reuse conditions and use your own reporting and appropriately licensed images.
- No paywall or block bypass. No automatic publication. No API keys are shipped.
- Apify execution may incur account usage charges. Start with one manual run.

## Local run
Python 3.12 recommended. `pip install -r requirements.txt`, then `python -m src.main`.
Local SDK input can be put in `storage/key_value_stores/default/INPUT.json`; otherwise the bundled INPUT.json is used. Output is in the local default key-value store.

## Validation
Run `python -m unittest discover -s tests`. Tests use mocked feed responses and workbook inspection, not live source requests. Live feed availability and an Apify cloud build remain deployment checks.
