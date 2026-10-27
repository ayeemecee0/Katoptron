#!/usr/bin/env python3
"""Structural source qualifications stay separate from any policy content fact."""
import importlib.util,json,unittest
from pathlib import Path
P=Path(__file__).with_name("inspect_wa_unreadable_originals.py")
spec=importlib.util.spec_from_file_location("held_wa_original_diagnostics",P)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
class SourceQualifications(unittest.TestCase):
 def test_original_registry_and_seven_exact_diagnoses(self):
  self.assertEqual(set(M.EXPECTED),{r["agency_name"] for r in M.SRC["receipts"] if r["inspection_status"].startswith("held")})
  self.assertEqual(len(M.EXPECTED),7)
  self.assertEqual(sum(bool(x["sha256_complete_original"]) for x in M.EXPECTED.values()),6)
  self.assertTrue(all(x["policy_page_content_verified"] is False for x in M.EXPECTED.values()))
 def test_six_hashes_and_one_size_bound_are_not_page_fact_evidence(self):
  for name,x in M.EXPECTED.items():
   inverse={
    "empty_page_content_streams":"EMPTY_PDF_PAGES_NO_CONTENT_STREAMS",
    "original_pdf_exceeds_16_mb_diagnostic_cap":"OVERSIZE_PDF_BYTE_CAP",
    "strict_parser_fails_image_pdf_lenient_only":"LENIENTLY_READABLE_IMAGE_ORIGINAL_STRICT_PDF_PARSE_FAILS",
    "pdf_reader_dependency_unresolved":"PDF_DEPENDENCY_UNRESOLVED",
    "manual_exceeds_160_page_triage_cap":"OVERSIZE_MANUAL_PAGE_COUNT"}
   r={"agency":name,"diagnosis":inverse[x["diagnosis"]],
      "sha256":x["sha256_complete_original"],
      "bytes":x["bytes_complete_original"] or x["minimum_observed_bytes"],
      "strict_true":{"page_count":x["page_count_structurally_readable"]},
      "strict_false":{"page_count":x["page_count_structurally_readable"]}}
   self.assertTrue(M.check_published_qualification(r),name)
   if x["sha256_complete_original"]:
    self.assertFalse(M.check_published_qualification({**r,"sha256":"0"*64}))
   self.assertFalse(M.check_published_qualification({**r,"diagnosis":"AGENCY_CONFIRMED_FLOCK_INSTALLED"}))
 def test_no_unreviewed_agency_facts_published(self):
  for x in M.EXPECTED.values():
   self.assertFalse(x["flock_vendor_confirmed"])
   self.assertFalse(x["device_location_published"])
   self.assertNotIn("operational_status",x)
if __name__=="__main__":unittest.main()
