#!/usr/bin/env python3
"""Render selected source-pinned Oklahoma City public contract pages for visual QA.

Only original government files with expected SHA-256 are rendered. QA images are
short-lived GitHub Actions artifacts, not published plate or camera data.
"""
import hashlib,json
from pathlib import Path
import fitz
from inspect_okc_2026_contract_originals import SOURCES,retrieve
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/".katoptron-ci"/"okc-original-2026-visual-review"
ORIGINALS={
"okc-2026-flock-amendment":("ed37e684252bec2c1938c3f927c777bf34ca67222c11ec86fccbd46da60f9ea0",2,[1,2]),
"okc-2026-flock-renewal-letter":("f2aa30d8b38fa8e35a88048d908f62162caaebf28bb12acc7291877ebe0d0ced",21,[1,19,20,21]),
"okc-2026-flock-council-memo":("fa6b7b8b81c1816ff5e09668af04d7160055a9385d1a8c844c74a2b174b4501e",2,[1,2]),
"okc-2026-funds-certificate":("1362ab7c9fe7e6902ed51657a616650ce0c6c8569fa553badacfb2be24c91b3c",1,[1])
}
def process(source,raw):
 expected,pages,page_ids=ORIGINALS[source]
 if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError("Original government PDF changed; review invalidated")
 pdf=fitz.open(stream=raw,filetype="pdf")
 if pdf.page_count!=pages:raise ValueError("Original government PDF page count changed")
 rec=[]
 for num in page_ids:
  page=pdf[num-1]
  pix=page.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False)
  if pix.width>3500 or pix.height>3500:raise ValueError("Unbounded original render")
  fname=f"{source}-page-{num:02d}.png"
  body=pix.tobytes("png")
  (OUT/fname).write_bytes(body)
  rec.append({"page":num,"png_sha256":hashlib.sha256(body).hexdigest(),
    "rendered_size_bytes":len(body),"image_file":fname})
 return {"id":source,"original_sha256":expected,"original_pages":pages,"rendered_page_receipts":rec}
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 results=[process(k,retrieve(k)) for k in ORIGINALS]
 (OUT/"visual-review-receipts.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf8")
 print("OKC_2026_SOURCE_PINNED_VISUAL_REVIEW",json.dumps(results,sort_keys=True))
if __name__=="__main__":main()
