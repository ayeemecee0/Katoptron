import importlib.util
from pathlib import Path
import hashlib
import unittest

spec=importlib.util.spec_from_file_location("mn_registry",Path(__file__).with_name("import_mn_alpr_audit_registry.py"))
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)

def page(n=24,misleading=False):
 rows=[]
 for i in range(n):
  label="Flock System" if i%4==0 else ("AXON System" if i%4==1 else "ALPR Program")
  name="Shakopee" if i==0 else "Sample Town "+str(i)
  title="Independent Auditor's Report: "+name+" Police Department "+label+" ALPR Audit"
  date="June 15, 2026"
  rid="26-"+str(1000+i).zfill(4)+".pdf"
  url="/docs/2026/mandated/26"+str(1000+i).zfill(4)+".pdf"
  rows.append('<tr><td>'+title+'</td><td>City of '+name+
   ' - Police Department<br>Auditor</td><td>'+date+
   '</td><td>2024 - 2026</td><td>06/17/2026</td><td><a href="'+url+'">'+rid+'</a></td></tr>')
 if misleading:
  rows.append('<tr><td>ALPR offsite</td><td></td><td></td><td></td><td></td><td><a href="https://evil.example/docs/2026/mandated/269999.pdf">26-9999.pdf</a></td></tr>')
 return ('<html><h1>Mandate Details</h1><table><thead><tr><th>Title</th><th>Publisher</th></tr></thead><tbody>'+
         ''.join(rows)+'</tbody></table></html>').encode()

class RegistryTests(unittest.TestCase):
 def test_safe_20_plus_entries_metadata_only(self):
  payload=page(misleading=True)
  rows=M.index_rows(payload)
  self.assertEqual(len(rows),24)
  self.assertTrue(all(r["source_url"].startswith("https://www.lrl.mn.gov/docs/2026/mandated/") for r in rows))
  self.assertTrue(all(r["evidence_tier"]=="state_legislative_registry_index_metadata_only" for r in rows))
  self.assertTrue(all(r["registry_sha256"]==hashlib.sha256(payload).hexdigest() for r in rows))
  self.assertEqual(sum(r["title_scope"]=="flock_named_in_title" for r in rows),6)
  self.assertEqual(sum(r["title_scope"]=="other_vendor_named_in_title" for r in rows),6)
  self.assertEqual(sum(r["title_scope"]=="unspecified_alpr_title" for r in rows),12)
  self.assertNotIn("execution_status",str(rows))
  self.assertNotIn("compliance_status",str(rows))
  self.assertNotIn("camera_coordinates",str(rows))
  first=next(r for r in rows if r["report_id"]=="26-1000.pdf")
  self.assertEqual(first["publication_date"],"2026-06-15")
  self.assertEqual(first["received_date"],"2026-06-17")
 def test_invalid_source_urls_and_fake_report_id_rejected(self):
  self.assertIsNone(M.normal_pdf_url("https://evil.example/docs/2026/mandated/261013.pdf","26-1013.pdf"))
  self.assertIsNone(M.normal_pdf_url("https://www.lrl.mn.gov/docs/2026/mandated/261013.pdf?x=1","26-1013.pdf"))
  self.assertIsNone(M.normal_pdf_url("/docs/2026/mandated/261013.pdf","26-1014.pdf"))
  self.assertIsNone(M.normal_pdf_url("/docs/2025/mandated/261013.pdf","26-1013.pdf"))
  self.assertIsNone(M.normal_pdf_url("http://www.lrl.mn.gov/docs/2026/mandated/261013.pdf","26-1013.pdf"))
  self.assertEqual(M.normal_pdf_url("/docs/2026/mandated/261013.pdf","26-1013.pdf"),
                   "https://www.lrl.mn.gov/docs/2026/mandated/261013.pdf")
 def test_registry_truncation_never_publishes(self):
  with self.assertRaisesRegex(ValueError,"Unexpected registry report count"):
   M.index_rows(page(19))
  with self.assertRaisesRegex(ValueError,"Unexpected registry report count"):
   M.index_rows(b'<html>maintenance page</html>')
 def test_index_conflicting_duplicate_id_held(self):
  data=page(24).decode()
  duplicate='<tr><td>Other Flock audit report</td><td>Agency</td><td>June 15, 2026</td><td></td><td>06/17/2026</td><td><a href="/docs/2026/mandated/261010.pdf">26-1010.pdf</a></td></tr>'
  # Repeated report IDs (including the same URL) cannot be silently merged.
  with self.assertRaisesRegex(ValueError,"duplicate report IDs"):
   M.index_rows(data.replace('</tbody>',duplicate+'</tbody>').encode())
 def test_without_database_key_cannot_publish(self):
  with self.assertRaisesRegex(ValueError,"credential unavailable"):
   M.publish(M.index_rows(page()),"https://example.supabase.co","")
 def test_other_vendors_never_become_flock_qualified(self):
  self.assertEqual(M.title_scope("ALPR Audit (AXON System)"),"other_vendor_named_in_title")
  self.assertEqual(M.title_scope("ALPR Audit (Flock System)"),"flock_named_in_title")
  self.assertEqual(M.title_scope("ALPR Audit (Flock and AXON Systems)"),"mixed_or_ambiguous_title")
  self.assertEqual(M.title_scope("Automated License Plate Reader Biennial Audit"),"unspecified_alpr_title")

if __name__=="__main__":unittest.main()
