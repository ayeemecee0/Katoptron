import importlib.util,hashlib,json,unittest
from pathlib import Path
P=Path(__file__).with_name('verify_agency_published_audits.py')
spec=importlib.util.spec_from_file_location('verified_self_audits',P)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
DATA=json.loads(M.MANIFEST.read_text())
class Page:
 def __init__(self,text):self.text=text
 def extract_text(self):return self.text
class Tests(unittest.TestCase):
 def test_curated_originals_are_bounded_and_separate_from_independent(self):
  rows=M.records(DATA)
  self.assertEqual(len(rows),4)
  self.assertEqual(set(x['state'] for x in rows),{'MN','CA','WI'})
  self.assertTrue(all(x['publisher_type']!='independent_external_audit' for x in rows))
 def test_official_host_source_id_and_date_guards(self):
  first=DATA['reports'][1]
  self.assertTrue(M.allowed(first))
  for url in ('http://www.sanbruno.ca.gov/DocumentCenter/View/9280/SBPD-Flock-ALPR-Annual-Audit---2025',
   'https://www.sanbruno.ca.gov.evil.example/DocumentCenter/View/9280/SBPD-Flock-ALPR-Annual-Audit---2025',
   first['source_url']+'?raw=true','https://evil.example/alpr.pdf','https://www.sanbruno.ca.gov@evil.example/alpr'):
   self.assertFalse(M.allowed({**first,'source_url':url}),url)
 def test_all_page_specific_verified_facts_fail_on_drift(self):
  raw=b'%PDF-1.7 synthetic agency reported source'+b'a'*200
  for record in DATA['reports']:
   anchors=M.ANCHORS[record['id']]
   class Reader:
    def __init__(self,*args,**kwargs):
     self.is_encrypted=False
     self.pages=[Page('original cover') for _ in range(4)]
     for n,tokens in anchors.items():self.pages[n-1]=Page(' '.join(tokens))
   fixture={**record,'content_sha256':hashlib.sha256(raw).hexdigest()}
   self.assertEqual(M.verify(fixture,raw,Reader),4)
   class Drift(Reader):
    def __init__(self,*args,**kwargs):
     super().__init__(*args,**kwargs)
     self.pages[next(iter(anchors))-1]=Page('Unrelated altered source')
   with self.assertRaisesRegex(ValueError,'changed'):M.verify(fixture,raw,Drift)
   with self.assertRaisesRegex(ValueError,'changed'):M.verify(record,raw,Reader)
 def test_an_internal_report_cannot_masquerade_as_external(self):
  forged={**DATA['reports'][0],'publisher_type':'independent_external_audit'}
  self.assertFalse(M.allowed(forged))
  with self.assertRaises(ValueError):M.records({**DATA,'reports':[forged]})
if __name__=='__main__':unittest.main()
