#!/usr/bin/env python3
import hashlib,importlib.util,json,unittest
from pathlib import Path
src=Path(__file__).with_name("verify_city_alpr_operational_statements.py")
spec=importlib.util.spec_from_file_location("agency_status_sources",src)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
DATA=json.loads(M.PATH.read_text(encoding="utf8"))
class TestOriginalCityStatusSources(unittest.TestCase):
 def test_exact_two_source_classifications(self):
  rows=M.catalog(DATA)
  self.assertEqual(len(rows),2)
  self.assertEqual({x["city"] for x in rows},{"Moline","Mill Valley"})
  self.assertIsNone(next(x for x in rows if x["city"]=="Moline")["effective_as_of"])
 def test_valid_html_and_byte_drift_metadata(self):
  for row in M.catalog(DATA):
   raw=("<html><body>"+" ".join(row["source_text_anchors"])+"</body></html>").encode()
   result=M.verify(row,raw)
   self.assertEqual(result["sha256"],hashlib.sha256(raw).hexdigest())
   self.assertTrue(result["original_html_changed"])
   with self.assertRaisesRegex(ValueError,"status source text"):
    M.verify(row,b"<html><body>unrelated source</body></html>"*8)
 def test_no_status_promotion_or_relabel(self):
  originals=M.catalog(DATA)
  moline=next(x for x in originals if x["city"]=="Moline")
  mill=next(x for x in originals if x["city"]=="Mill Valley")
  for target,m in [(moline,{**moline,"effective_as_of":"2026-09-29"}),
                   (moline,{**moline,"classification":mill["classification"]}),
                   (mill,{**mill,"agency":"San Bruno Police Department"}),
                   (mill,{**mill,"statement_published_on":"2026-09-09"})]:
   with self.assertRaisesRegex(ValueError,"identity, date, or status"):
    M.catalog({**DATA,"documents":[m if x["id"]==target["id"] else x for x in originals]})
 def test_reject_unlisted_url(self):
  with self.assertRaisesRegex(ValueError,"Unapproved"):M.fetch("https://evil.example/1955/License-Plate-Readers")
if __name__=="__main__":unittest.main()
