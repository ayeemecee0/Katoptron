#!/usr/bin/env python3
import json
import unittest
from pathlib import Path
from review_wa_flock_original_pages import (
    REGISTRY, SNAPSHOT, review, run, selected, term_page_match,
)
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf8"))
        cls.snapshot = json.loads(SNAPSHOT.read_text(encoding="utf8"))
    def test_source_pinned_candidates(self):
        rows = selected(self.snapshot, self.registry)
        self.assertEqual(len(rows), 10)
        self.assertEqual(len({r["agency_name"] for r in rows}), 10)
        self.assertTrue(all(r["potential_flock_term_pages"] for r in rows))
        self.assertTrue(all(len(r["sha256"]) == 64 for r in rows))
    def test_term_detection_has_boundaries(self):
        self.assertTrue(term_page_match("Use of Flock Safety is subject to procedure."))
        self.assertTrue(term_page_match("Flock   Safety portal."))
        self.assertFalse(term_page_match("flocking safety measures"))
        self.assertFalse(term_page_match("An ALPR manufacturer was not identified."))
    def test_invalid_or_missing_pdf_never_creates_claim(self):
        row = selected(self.snapshot, self.registry)[0]
        result = review(row, lambda _: b"not a pdf" * 50)
        self.assertEqual(result["status"], "held_wrong_document")
        self.assertFalse(result["actual_vendor_deployment_verified"])
        self.assertEqual(result["new_camera_coordinates"], 0)
        self.assertEqual(review(row, lambda _: b"%PDF-" + b"fake" * 100)["status"],
                         "held_original_sha_changed")
        self.assertEqual(review(row, lambda _: (_ for _ in ()).throw(OSError()))["status"],
                         "held_unreachable")
    def test_pipeline_fail_closed(self):
        report = run(self.snapshot, self.registry, lambda _: b"invalid" * 50,
                     checked_at="2026-10-28T00:00:00+00:00")
        self.assertEqual(report["candidate_originals"], 10)
        self.assertEqual(report["source_pages_rechecked_successfully"], 0)
        self.assertEqual(report["source_page_recheck_holds"], 10)
        self.assertEqual(report["new_verified_flock_deployments"], 0)
        self.assertEqual(report["new_adopted_policy_changes"], 0)
        self.assertTrue(all("text" not in r for r in report["records"]))
        modified = json.loads(json.dumps(self.snapshot))
        modified["receipts"][0]["manufacturer_identity_assertion"] = True
        with self.assertRaises(ValueError): selected(modified, self.registry)
if __name__ == "__main__":
    unittest.main()
