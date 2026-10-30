import io
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from openpyxl import load_workbook
from src.main import canonical, make_row, workbook, collect, cricbuzz_entry, NewsLinks

class CollectorTests(unittest.IsolatedAsyncioTestCase):
    def test_rows_and_excel(self):
        now = datetime.now(timezone.utc)
        row = make_row({'title':'=HYPERLINK("bad")','link':'https://example.com/news?utm_source=x','summary':'<p>Reference</p>'},'Test',now,now-timedelta(hours=72))
        self.assertEqual(row['Source URL'],'https://example.com/news')
        self.assertIn('Missing',row['Date check'])
        wb=load_workbook(io.BytesIO(workbook([row],[])))
        self.assertEqual(wb['Stories']['C2'].data_type,'s')
        self.assertEqual(wb['Stories']['H2'].value,'Reference')
        self.assertEqual(wb['Stories']['L2'].value,'New')
        self.assertEqual(len(wb['Stories'].data_validations.dataValidation),1)
    async def test_collection_and_failures(self):
        import httpx
        feed='<rss version="2.0"><channel><title>Cricket</title><item><title>Match preview</title><link>https://example.com/a?utm_source=test</link></item><item><title>Duplicate</title><link>https://example.com/a</link></item></channel></rss>'
        def respond(request):
            return httpx.Response(200,text=feed) if request.url.host=='www.espncricinfo.com' else httpx.Response(403)
        original = httpx.AsyncClient
        with patch('src.main.httpx.AsyncClient',side_effect=lambda **kw:original(transport=httpx.MockTransport(respond),**kw)):
            rows, reports=await collect({'sources':[{'name':'Good','url':'https://good.example/rss'},{'name':'Bad','url':'https://bad.example/rss'}]})
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['Suggested type'],'Preview')
        self.assertEqual([r['Status'] for r in reports],['OK','Failed'])
        self.assertEqual(rows[0]['Source'],'ESPNcricinfo')
        self.assertEqual([r['Source'] for r in reports],['ESPNcricinfo','Cricbuzz'])
    def test_old_story_filtered(self):
        now=datetime.now(timezone.utc)
        self.assertIsNone(make_row({'title':'Old','link':'https://example.com/old','published_parsed':(2020,1,1,0,0,0,0,0,0)},'Test',now,now-timedelta(hours=72)))

    def test_cricbuzz_metadata_and_links(self):
        parser=NewsLinks();parser.feed('<a href="/cricket-news/123/story"><h2>India squad</h2></a><a href="/live-cricket-scores/123">Score</a>')
        self.assertEqual(parser.links,[('https://www.cricbuzz.com/cricket-news/123/story','India squad')])
        html='''<meta property="og:title" content="Fallback"><script type="application/ld+json">{"@graph":[{"@type":"NewsArticle","headline":"India squad announced","description":"Two spinners included.","datePublished":"2026-10-30T09:00:00+05:30","articleSection":"News"}]}</script>'''
        entry=cricbuzz_entry(html,'https://www.cricbuzz.com/cricket-news/123/story','Link text')
        self.assertEqual(entry['title'],'India squad announced')
        self.assertEqual(entry['summary'],'Two spinners included.')
        self.assertEqual(entry['published_parsed'][:6],(2026,10,30,3,30,0))
        self.assertEqual(entry['tags'],[{'term':'News'}])
        fallback=cricbuzz_entry('<meta property="og:title" content="Headline"><meta property="og:description" content="Summary">','https://www.cricbuzz.com/cricket-news/124/story','Fallback')
        self.assertEqual(fallback['title'],'Headline');self.assertNotIn('published_parsed',fallback)

    async def test_cricbuzz_collection_keeps_source_and_handles_partial_failure(self):
        import httpx
        feed='<rss version="2.0"><channel><title>Cricket</title></channel></rss>'
        listing='<a href="/cricket-news/1/story">Story</a><a href="/cricket-news/2/failed">Other</a>'
        def respond(request):
            if request.url.host=='www.espncricinfo.com': return httpx.Response(200,text=feed)
            if request.url.path=='/cricket-news': return httpx.Response(200,text=listing)
            if request.url.path=='/cricket-news/1/story': return httpx.Response(200,text='<meta property="og:title" content="Squad announced"><meta property="og:description" content="Two players return">')
            return httpx.Response(403)
        original=httpx.AsyncClient
        with patch('src.main.httpx.AsyncClient',side_effect=lambda **kw:original(transport=httpx.MockTransport(respond),**kw)):
            rows,reports=await collect({'maxItemsPerSource':2})
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['Source'],'Cricbuzz')
        self.assertEqual(reports[1]['Status'],'Warning');self.assertIn('1 article pages failed',reports[1]['Detail'])
