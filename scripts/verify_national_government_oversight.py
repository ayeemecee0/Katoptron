#!/usr/bin/env python3
"""Verify original government oversight and agency-authored impact assessments.

The byte-pinned ORIGINAL government PDF and auditor page text must match
reviewed provenance. Different publisher roles are never conflated.
"""
import hashlib
import json
import re
from pathlib import Path
from inspect_national_oversight_originals import ORIGINALS, fetch, inspect, allowed

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"data"/"verified-national-government-oversight.json"
PAGES={"san-mateo-ca-2026-grand-jury":20,
       "austin-tx-2025-city-auditor":21,
       "woodburn-or-2026-impact-assessment":98}

def records(doc):
 if not isinstance(doc,dict) or doc.get("schema_version")!=1 or not isinstance(doc.get("reports"),list) or len(doc["reports"])!=3:
  raise ValueError("Incomplete original government oversight catalog")
 ids=set(); urls=set()
 for r in doc["reports"]:
  key=r.get("id")
  if key in ids or key not in ORIGINALS:raise ValueError("Unapproved original oversight report ID")
  ids.add(key)
  if r.get("source_url")!=ORIGINALS[key]["url"] or not allowed(key,r["source_url"]) or r["source_url"] in urls:
   raise ValueError("Original government authority URL changed")
  urls.add(r["source_url"])
  if r.get("publisher_type")!=ORIGINALS[key]["publisher_type"] or r.get("state")!=ORIGINALS[key]["state"]:
   raise ValueError("Government reviewer independence tier cannot be promoted")
  if not re.fullmatch(r"[a-f0-9]{64}",r.get("content_sha256","")):
   raise ValueError("Original PDF byte digest missing")
  if not isinstance(r.get("pages_reviewed"),list) or not set(ORIGINALS[key]["anchors"]).issubset(set(r["pages_reviewed"])):
   raise ValueError("Review page anchors missing")
  if r.get("source_date") is not None and not re.fullmatch(r"20\d{2}-\d{2}-\d{2}",r.get("source_date","")):
   raise ValueError("Unknown original publication dates must remain unknown")
  if r.get("source_date") is None and len(r.get("source_date_note",""))<20:
   raise ValueError("Uncertain dates need an explanation")
  if not isinstance(r.get("findings"),list) or not 1<=len(r["findings"])<=8:raise ValueError("Unbounded findings")
  for f in r["findings"]:
   if not isinstance(f,dict) or f.get("page") not in r["pages_reviewed"] or not 55<=len(f.get("statement",""))<=950:
    raise ValueError("Missing bounded original page finding")
 return doc["reports"]

def verify(r,raw,reader=None):
 if hashlib.sha256(raw).hexdigest()!=r["content_sha256"]:
  raise ValueError("Original oversight PDF SHA changed; hold findings")
 info=inspect(r["id"],raw,reader=reader) if reader is not None else inspect(r["id"],raw)
 if info["pages"]!=PAGES[r["id"]] or not info["anchors_match"]:
  raise ValueError("Original government oversight pages changed; hold findings")
 return info

def main():
 doc=json.loads(MANIFEST.read_text(encoding="utf-8"))
 for report in records(doc):
  v=verify(report,fetch(report["id"]))
  print("GOVERNMENT_OVERSIGHT_ORIGINAL_VERIFIED",report["id"],"STATE",report["state"],
     "PAGES",v["pages"],"SHA256",v["sha256"],"ROLE",report["publisher_type"])
 print("ALL PINNED ORIGINAL GOVERNMENT OVERSIGHT PAGES PASS; no personal plate records, inferred map pins or data sharing edges")
if __name__=="__main__":
 try:main()
 except Exception as e:
  raise SystemExit("Original government oversight verification held: "+type(e).__name__+": "+str(e)[:180]) from None
