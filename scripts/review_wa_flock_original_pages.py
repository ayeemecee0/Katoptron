#!/usr/bin/env python3
"""Recheck source-pinned Flock Safety phrase pages, NOT Flock deployments.

All source text stays in memory: the public report contains only source metadata,
original-source PDF page locations, and machine-text term-match outcomes.
This is an acquisition/review queue, never an adoption or operating-status feed.
"""
import datetime as dt
import hashlib
import io
import json
import re
from pathlib import Path
from pypdf import PdfReader
from triage_wa_ago_policy_origins import (
    REGISTRY, ROOT, candidates, fetch, validate_snapshot,
)

SNAPSHOT = ROOT / "data" / "wa-ago-original-policy-source-inspection.json"
OUT = ROOT / ".katoptron-ci" / "wa-flock-term-page-rechecks.json"
MATCH = re.compile(r"\bflock\s+safety\b", re.IGNORECASE)
MAX_BYTES = 8_000_000
MAX_PAGES = 160

def selected(snapshot, registry):
    validated = validate_snapshot(snapshot, registry)
    selected_rows = [r for r in validated["receipts"]
                     if r["inspection_status"] == "exact_pdf_text_detected"
                     and r["potential_flock_term_pages"]]
    # Strict baseline: new candidates require explicit editorial reconciliation.
    if len(selected_rows) != 10:
        raise ValueError("Original 10-candidate review baseline changed")
    return selected_rows

def term_page_match(text):
    """Only a literal manufacturer name occurrence, not a factual conclusion."""
    return bool(MATCH.search(" ".join((text or "").split())))

def review(row, fetcher=fetch):
    result = {
        "agency": row["agency_name"], "original_url": row["policy_source_url"],
        "observed_source_sha256": row["sha256"],
        "expected_original_pages": row["page_count"],
        "candidate_pages": list(row["potential_flock_term_pages"]),
        "status": "held_unreachable", "matched_original_pages": [],
        "actual_vendor_deployment_verified": False,
        "enacted_policy_verified": False,
        "live_data_sharing_verified": False, "new_camera_coordinates": 0,
    }
    try:
        raw = fetcher(row["policy_source_url"])
    except Exception:
        return result
    if not isinstance(raw, bytes) or not 100 < len(raw) <= MAX_BYTES or not raw.startswith(b"%PDF-"):
        result["status"] = "held_wrong_document"
        return result
    if hashlib.sha256(raw).hexdigest() != row["sha256"]:
        result["status"] = "held_original_sha_changed"
        return result
    try:
        doc = PdfReader(io.BytesIO(raw), strict=True)
        if doc.is_encrypted or not 1 <= len(doc.pages) <= MAX_PAGES or len(doc.pages) != row["page_count"]:
            result["status"] = "held_original_structure_changed"
            return result
        matched = []
        for p in row["potential_flock_term_pages"]:
            if term_page_match(doc.pages[p - 1].extract_text() or ""):
                matched.append(p)
        if matched != row["potential_flock_term_pages"]:
            result["status"] = "held_term_page_mismatch"
        else:
            result["status"] = "exact_original_pdf_sha_and_term_pages_matched_review_candidate"
            result["matched_original_pages"] = matched
    except Exception:
        result["status"] = "held_pdf_parse_error"
    return result

def run(snapshot, registry, fetcher=fetch, checked_at=None):
    rows = selected(snapshot, registry)
    results = [review(row, fetcher) for row in rows]
    matched = sum(r["status"].startswith("exact_original_pdf_sha") for r in results)
    return {
        "schema_version": 1,
        "checked_at": checked_at or dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope": "exact_original_pdf_SHA_and_Flock_Safety_phrase_page_recheck_only",
        "candidate_originals": len(results),
        "source_pages_rechecked_successfully": matched,
        "source_page_recheck_holds": len(results) - matched,
        "new_verified_flock_deployments": 0,
        "new_adopted_policy_changes": 0,
        "new_camera_coordinates": 0,
        "records": results,
    }

def main():
    registry = json.loads(REGISTRY.read_text(encoding="utf8"))
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf8"))
    report = run(snapshot, registry)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
    print("WA_FLOCK_ORIGINAL_TERM_PAGE_RECHECK", json.dumps({
        k: report[k] for k in ("candidate_originals",
            "source_pages_rechecked_successfully", "source_page_recheck_holds",
            "new_verified_flock_deployments", "new_adopted_policy_changes",
            "new_camera_coordinates")}, sort_keys=True))
    for row in report["records"]:
        print("SOURCE_PAGE_REVIEW", json.dumps({
            "agency": row["agency"], "status": row["status"],
            "matched_original_pages": row["matched_original_pages"]}, sort_keys=True))

if __name__ == "__main__":
    main()
