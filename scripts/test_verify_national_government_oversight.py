import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

P=Path(__file__).with_name('verify_national_government_oversight.py')
spec=importlib.util.spec_from_file_location('orig_government_oversight',P)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
DATA=json.loads(M.MANIFEST.read_text())
class Page:
 def __init__(self,text):self.text=text
 def extract_text(self):return self.text
class TestNationalOversight(unittest.TestCase):
 def test_exact_publication_provenance_and_publisher_classification(self):
  rows=M.records(DATA)
  self.assertEqual(len(rows),3)
  self.assertEqual({r['state'] for r in rows},{'CA','TX','OR'})
  self.assertEqual(sum(r['publisher_type']=='independent_government_oversight' for r in rows),2)
  self.assertEqual(sum(r['publisher_type']=='agency_authored_impact_assessment' for r in rows),1)
  self.assertIsNone(next(r for r in rows if r['state']=='TX')['source_date'])
 def test_originals_are_exact_and_altered_source_is_held(self):
  raw=b'%PDF-1.7\n'+b'x'*400
  for row in M.records(DATA):
   key=row['id']
   anchors=M.ORIGINALS[key]['anchors']
   class Reader:
    def __init__(self,*args,**kwargs):
     self.is_encrypted=False
     self.pages=[Page("filler") for _ in range(M.PAGES[key])]
     for p,phrases in anchors.items():self.pages[p-1]=Page(" ".join(phrases))
   r={**row,'content_sha256':hashlib.sha256(raw).hexdigest()}
   self.assertTrue(M.verify(r,raw,Reader)['anchors_match'])
   with self.assertRaisesRegex(ValueError,'SHA changed'):M.verify(row,raw,Reader)
   class Drift(Reader):
    def __init__(self,*args,**kwargs):
     super().__init__(*args,**kwargs)
     self.pages[next(iter(anchors))-1]=Page("Unexpected source revision")
   with self.assertRaisesRegex(ValueError,'pages changed'):M.verify(r,raw,Drift)
 def test_no_fake_independent_review_or_non_government_url(self):
  original=DATA['reports'][2]
  forged={**original,'publisher_type':'independent_government_oversight'}
  with self.assertRaisesRegex(ValueError,'independence tier'):M.records({...DATA,'reports':[DATA['reports'][0],DATA['reports'][1],forged]})
  attacker={**original,'source_url':'https://www.woodburn-or.gov.evil.example/secret.pdf'}
  with self.assertRaisesRegex(ValueError,'authority URL'):M.records({...DATA,'reports':[DATA['reports'][0],DATA['reports'][1],attacker]})
if __name__=='__main__':unittest.main()
