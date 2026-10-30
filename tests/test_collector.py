import io
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from openpyxl import load_workbook
from src.main import canonical, make_row, workbook, collect

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
            return httpx.Response(200,text=feed) if request.url.host=='good.example' else httpx.Response(403)
        original = httpx.AsyncClient
        with patch('src.main.httpx.AsyncClient',side_effect=lambda **kw:original(transport=httpx.MockTransport(respond),**kw)):
            rows, reports=await collect({'sources':[{'name':'Good','url':'https://good.example/rss'},{'name':'Bad','url':'https://bad.example/rss'}]})
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['Suggested type'],'Preview')
        self.assertEqual([r['Status'] for r in reports],['OK','Failed'])
    def test_old_story_filtered(self):
        now=datetime.now(timezone.utc)
        self.assertIsNone(make_row({'title':'Old','link':'https://example.com/old','published_parsed':(2020,1,1,0,0,0,0,0,0)},'Test',now,now-timedelta(hours=72)))
