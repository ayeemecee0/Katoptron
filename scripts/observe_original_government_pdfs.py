#!/usr/bin/env python3
"""Private, bounded byte-level receipts for original-government PDF leads.

Retrieval proves only which bytes a public original-government URL served at
one instant. NEVER publishes contract facts, sharing grants, dates, camera
coordinates, or per-device manufacturer claims; NEVER stores PDF bytes/text.
"""
import datetime as dt
import hashlib
import os
import re
import urllib.parse

from acquire_original_government_documents import (
    MAX_PAGE, fetch, normalize_url, page_all, rest,
)

MAX_PDF_BYTES = 6_000_000
MAX_DOCUMENTS_PER_RUN = 12
UTC = dt.timezone.utc

def pdf_link_candidate(row):
    """Only link-scoped original .gov PDF candidates; no arbitrary URLs."""
    url = str(row.get("document_url") or "")
    page = str(row.get("government_page_url") or "")
    label = str(row.get("link_label") or "")
    if row.get("review_status") not in (
        "requires_document_review", "extracted_recipient_candidate",
        "document_content_verified",
    ):
        return False
    gov_host = urllib.parse.urlsplit(page).hostname
    if not gov_host or not gov_host.endswith(".gov"):
        return False
    if normalize_url(url, page, gov_host) != url:
        return False
    return bool(
        re.search(r"\.pdf$", urllib.parse.urlsplit(url).path, re.I)
        or re.search(r"\bpdf\b", label, re.I)
    )

def select_due(leads, attempts, now=None, limit=MAX_DOCUMENTS_PER_RUN):
    """No starvation: unseen URLs first, failed URLs only after cooldown."""
    now = now or dt.datetime.now(UTC)
    candidates = []
    for row in leads:
        if not pdf_link_candidate(row):
            continue
        prior = attempts.get(row["document_url"])
        if prior:
            try:
                due = dt.datetime.fromisoformat(
                    prior["next_retry_at"].replace("Z", "+00:00"))
                if due.tzinfo is None or due > now:
                    continue
            except (ValueError, KeyError, TypeError, AttributeError):
                continue  # Corrupt attempts fail closed; do not hot-loop
        candidates.append((bool(prior), row["document_url"], row))
    candidates.sort(key=lambda x: (x[0], x[1]))
    return [row for _, _, row in candidates[:limit]]

def pdf_digest(payload, content_type):
    """PDF header and tail checks, not text/content or legal verification."""
    if not isinstance(payload, bytes) or not 32 <= len(payload) <= MAX_PDF_BYTES:
        return None
    media = (content_type or "").split(";", 1)[0].strip().lower()
    if media not in ("application/pdf", "application/octet-stream", "binary/octet-stream"):
        return None
    if not re.match(rb"^%PDF-[12]\.[0-9]", payload[:16]):
        return None
    if b"%%EOF" not in payload[-2048:]:
        return None
    return hashlib.sha256(payload).hexdigest()

def inspect(rows, attempts, fetcher=fetch, now=None):
    """Produce private receipts and bounded retry results; no PDF data escape."""
    now = now or dt.datetime.now(UTC)
    receipts, updates = [], []
    due = select_due(rows, attempts, now=now)
    stamp = now.isoformat()
    for row in due:
        url = row["document_url"]
        outcome = "held_fetch_error"
        sha = None
        size = 0
        try:
            payload, media = fetcher(url, MAX_PDF_BYTES)
            sha = pdf_digest(payload, media)
            if sha:
                size = len(payload)
                outcome = "pdf_bytes_observed"
            else:
                outcome = "held_non_pdf_or_invalid_bytes"
        except Exception:
            pass  # No exception strings or response bodies in logs/metrics
        if sha:
            receipts.append({
                "document_url": url,
                "content_sha256": sha,
                "byte_length": size,
                "observed_media_type": "application/pdf",
                "evidence_tier": "downloaded_pdf_bytes_only",
                "last_observed_at": stamp,
            })
        # Recheck observed bytes within 14d, bad MIME after 30d, outages
        # after 7d. Failing sites cannot starve never-tried sources.
        retry_days = (14 if sha else
                      30 if outcome == "held_non_pdf_or_invalid_bytes" else 7)
        updates.append({
            "document_url": url,
            "last_checked_at": stamp,
            "last_outcome": outcome,
            "next_retry_at": (now + dt.timedelta(days=retry_days)).isoformat(),
        })
    return receipts, updates

def main():
    api = os.environ.get("SUPABASE_URL", "")
    secret = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not api or not secret:
        raise RuntimeError("Private document receipt credential missing")
    leads = page_all(api, secret, "flock_original_document_leads",
                     "document_url,government_page_url,link_label,review_status")
    prior = page_all(api, secret, "flock_original_pdf_attempts",
                     "document_url,next_retry_at")
    receipts, checked = inspect(leads, {r["document_url"]: r for r in prior})
    for item in receipts:
        rest(api, secret, "flock_original_document_pdf_receipts", method="POST",
             params={"on_conflict": "document_url,content_sha256"},
             body=[item], prefer="resolution=merge-duplicates,return=minimal")
    for item in checked:
        rest(api, secret, "flock_original_pdf_attempts", method="POST",
             params={"on_conflict": "document_url"},
             body=[item], prefer="resolution=merge-duplicates,return=minimal")
    rest(api, secret, "flock_original_pdf_scan_runs", method="POST",
         body=[{
             "documents_attempted": len(checked),
             "pdf_bytes_observed": len(receipts),
             "documents_held": len(checked) - len(receipts),
         }], prefer="return=minimal")
    observed = page_all(api, secret, "flock_original_document_pdf_receipts",
                        "document_url,content_sha256")
    total = len({x["document_url"] for x in observed})
    day = dt.datetime.now(UTC).date().isoformat()
    # Existing daily page-acquisition metrics persist; PATCH exactly one
    # aggregate count without overwriting unrelated source measurements.
    rest(api, secret, "flock_original_acquisition_public_metrics",
         method="PATCH", params={"metric_date": "eq." + day},
         body={"pdf_downloaded_unreviewed_documents": total},
         prefer="return=minimal")
    print("Original PDF candidate pages:", len(leads),
          "PDF links attempted:", len(checked),
          "PDF bytes observed:", len(receipts),
          "held (not PDF or unavailable):", len(checked)-len(receipts),
          "distinct historical PDF byte receipts:", total,
          "independently content-verified by this job: 0")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit("Original PDF byte acquisition held: "+
                         type(exc).__name__) from None
