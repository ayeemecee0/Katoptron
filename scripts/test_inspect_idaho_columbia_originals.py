#!/usr/bin/env python3
import importlib.util,io,unittest
from pathlib import Path
from pypdf import PdfWriter
P=Path(__file__).with_name("inspect_idaho_columbia_originals.py")
s=importlib.util.spec_from_file_location("original_state_sources",P)
M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
def blank_pdf(pages):
 w=PdfWriter()
 for _ in range(pages):w.add_blank_page(width=612,height=792)
 out=io.BytesIO();w.write(out);return out.getvalue()
class OriginalSourceTests(unittest.TestCase):
 def test_original_allowlist_and_status(self):
  self.assertEqual(len(M.SOURCES),2)
  self.assertEqual({x["state"] for x in M.SOURCES.values()},{"ID","MO"})
  for row in M.SOURCES.values():
   self.assertTrue(row["url"].startswith("https://"))
   self.assertTrue(row["url"].split("/")[2].endswith(".gov"))
  with self.assertRaisesRegex(ValueError,"Unknown original"):
   M.fetch("https://evil.example/path")
 def test_receipts_are_not_adoption_or_camera_facts(self):
  docs={s["url"]:blank_pdf(s["pages"]) for s in M.SOURCES.values()}
  result=M.inspect(fetcher=lambda url:docs[url])
  self.assertEqual(len(result),2)
  self.assertEqual(result[0]["page_count"],2)
  self.assertEqual(result[1]["page_count"],9)
  self.assertEqual(result[0]["page_receipts"][0]["page"],1)
  self.assertTrue(all(r["agency_policy_adoption_verified"] is False for r in result))
  self.assertTrue(all(r["current_operational_platform_verified"] is False for r in result))
  self.assertTrue(all(r["camera_locations_published"]==0 for r in result))
 def test_wrong_length_or_format_is_held(self):
  with self.assertRaisesRegex(ValueError,"size or format|PDF receipt"):
   M.inspect(fetcher=lambda url:b"<html>untrusted</html>")
 def test_wrong_page_count_is_held(self):
  sample=blank_pdf(1)
  with self.assertRaisesRegex(ValueError,"page count"):
   M.inspect(fetcher=lambda url:sample)
if __name__=="__main__":unittest.main()
