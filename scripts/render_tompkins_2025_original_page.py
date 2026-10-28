#!/usr/bin/env python3
"""Render only the government-PDF original page used for Tompkins historical use.

Source PDF exact SHA-256 and page count bound the original. Output is a QA
visual artifact, not a new camera point or plate record.
"""
import hashlib,json
from pathlib import Path
from preflight_ny_wv_original_flock_records import retrieve,SOURCES
OUT=Path(__file__).resolve().parents[1]/".katoptron-ci"/"ny-tompkins-2025-source-review"
SHA="a44d7a11f61c62508936cbc43ff1233cad2849929e81afd482046e6f47f94988"
def main():
 import fitz
 b=retrieve("ny-tompkins-sheriff-july2025-report")
 if hashlib.sha256(b).hexdigest()!=SHA:raise ValueError("Original government monthly report changed")
 pdf=fitz.open(stream=b,filetype="pdf")
 if pdf.page_count!=8:raise ValueError("Official eight-page July report page count changed")
 page=pdf[6]
 pix=page.get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False)
 png=pix.tobytes("png")
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"official-source-page-07.png").write_bytes(png)
 meta={"government_source_sha256":SHA,"government_original_pages":8,
 "reviewed_original_page":7,"rendered_page_png_sha256":hashlib.sha256(png).hexdigest(),
 "page_image_bytes":len(png),"source_url":SOURCES["ny-tompkins-sheriff-july2025-report"]["source_url"]}
 (OUT/"source-visual-review-receipt.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf8")
 print("NY_TOMPKINS_ORIGINAL_PDF_VISUAL_PAGE_REVIEW",json.dumps(meta,sort_keys=True))
if __name__=="__main__":main()
