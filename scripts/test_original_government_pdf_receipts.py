"""Original-government PDF byte verification is intentionally not fact review."""
import datetime as dt
import importlib.util
from pathlib import Path
import unittest

P=Path(__file__).with_name("observe_original_government_pdfs.py")
spec=importlib.util.spec_from_file_location("original_gov_pdf_bytes", P)
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
NOW=dt.datetime(2026,10,25,20,0,tzinfo=dt.timezone.utc)

def lead(suffix, *, label="Flock policy PDF", review="requires_document_review"):
    return {
        "document_url": "https://portagein.gov/files/"+suffix,
        "government_page_url": "https://portagein.gov/547/Flock-Information-Center",
        "link_label":label,
        "review_status":review,
    }

PDF=b"%PDF-1.7\n"+b"0 1 obj\n<< /Type /Catalog >>\nendobj\n"+b"%%EOF\n"

class OriginalPDFReceipts(unittest.TestCase):
    def test_pdf_magic_mime_and_bounded_retrieval(self):
        self.assertEqual(len(M.pdf_digest(PDF, "application/pdf")), 64)
        self.assertEqual(M.pdf_digest(PDF, "application/octet-stream"),
                         M.pdf_digest(PDF, "application/pdf"))
        self.assertIsNone(M.pdf_digest(PDF, "text/html"))
        self.assertIsNone(M.pdf_digest(b"<html>PDF login page</html>", "application/pdf"))
        self.assertIsNone(M.pdf_digest(PDF.replace(b"%%EOF",b"incorrect"), "application/pdf"))
        self.assertIsNone(M.pdf_digest(PDF+b"z"*(M.MAX_PDF_BYTES+1),"application/pdf"))

    def test_original_host_boundary_and_link_type(self):
        self.assertTrue(M.pdf_link_candidate(lead("a.pdf")))
        self.assertFalse(M.pdf_link_candidate(lead("a.html",label="Page")))
        self.assertFalse(M.pdf_link_candidate({
            **lead("a.pdf"), "document_url":"https://other-town.gov/a.pdf"}))
        self.assertFalse(M.pdf_link_candidate({
            **lead("a.pdf"), "document_url":"http://portagein.gov/a.pdf"}))
        self.assertFalse(M.pdf_link_candidate(lead("a.pdf",review="rejected")))
        self.assertTrue(M.pdf_link_candidate(lead("download?id=3")))

    def test_fair_queue_never_repeats_held_before_new(self):
        leads=[lead("a.pdf"),lead("b.pdf"),lead("c.pdf")]
        prior={"https://portagein.gov/files/a.pdf":{
            "next_retry_at":(NOW+dt.timedelta(days=7)).isoformat()}}
        queued=M.select_due(leads,prior,NOW,limit=10)
        self.assertEqual([x["document_url"].split("/")[-1] for x in queued],
                         ["b.pdf","c.pdf"])
        prior["https://portagein.gov/files/a.pdf"]["next_retry_at"]=(
            NOW-dt.timedelta(days=1)).isoformat()
        queued=M.select_due(leads,prior,NOW,limit=10)
        self.assertEqual([x["document_url"].split("/")[-1] for x in queued],
                         ["b.pdf","c.pdf","a.pdf"])

    def test_failures_hold_without_changing_document_review(self):
        rows=[lead("a.pdf"),lead("b.pdf"),lead("c.pdf")]
        def fetcher(url,limit):
            self.assertEqual(limit,M.MAX_PDF_BYTES)
            if url.endswith("a.pdf"):
                return PDF,"application/pdf"
            if url.endswith("b.pdf"):
                return b"<html>Login</html>","text/html"
            raise OSError("403")
        receipts,attempts=M.inspect(rows,{},fetcher,NOW)
        self.assertEqual(len(receipts),1)
        self.assertEqual(len(attempts),3)
        self.assertEqual(receipts[0]["evidence_tier"],"downloaded_pdf_bytes_only")
        self.assertEqual(receipts[0]["byte_length"],len(PDF))
        self.assertNotIn("document_bytes",receipts[0])
        self.assertNotIn("contract_amount",receipts[0])
        self.assertNotIn("retention_days",receipts[0])
        self.assertNotIn("camera_latitude",receipts[0])
        self.assertEqual({x["last_outcome"] for x in attempts},
          {"pdf_bytes_observed","held_non_pdf_or_invalid_bytes","held_fetch_error"})
        self.assertTrue(all(x["next_retry_at"]>x["last_checked_at"] for x in attempts))
        self.assertTrue(all(x["review_status"]=="requires_document_review" for x in rows))

if __name__=="__main__":
    unittest.main()
