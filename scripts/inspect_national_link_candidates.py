#!/usr/bin/env python3
"""Read-only original government PDF content triage for the nine source watch leads.
Original publisher HTTPS only; no redirects or personal plate/subject log content.
The script can output a bounded excerpt of policy/order/aggregate items for
curation. Nothing is promoted into public verified facts automatically.
"""
import io,hashlib,json,re,urllib.request,urllib.parse
from pypdf import PdfReader
SOURCES={
 "san-mateo-ca-press-advisory":("https://sanmateo.courts.ca.gov/system/files/grand-jury/alpr-press-release.pdf",[1,2]),
 "austin-tx-auditor-slides":("https://services.austintexas.gov/edims/document.cfm?id=452702",[1,5,9]),
 "green-bay-wi-monthly-2026":("https://www.greenbaywi.gov/DocumentCenter/View/18823/Green-Bay-Police-Department-Monthly-ALPR-Report-September-2026",[1]),
 "san-bruno-ca-alpr-policy":("https://www.sanbruno.ca.gov/DocumentCenter/View/9522/San-Bruno-PD---ALPR-Policy",[1,2,4]),
 "austin-tx-oversight-memo-2023":("https://services.austintexas.gov/edims/document.cfm?id=452776",[1,2,3]),
 "green-bay-wi-policy-may-2026":("https://www.greenbaywi.gov/DocumentCenter/View/18791/Policy-424-Automated-License-Plate-Readers-ALPR-May-2026",[1,2,3,4]),
 "green-bay-wi-policy-draft-sept-2026":("https://www.greenbaywi.gov/DocumentCenter/View/19136/DRAFTED-REVISION---Policy-424-Automated-License-Plate-Readers-ALPR-September-2026",[1,2,3,4,5,6]),
 "green-bay-wi-flock-order-2025":("https://www.greenbaywi.gov/DocumentCenter/View/19138/Flock-Safety-WI---Green-Bay-PD---DFR-and-ALPR-Law-Enforcement-Agreement-2025",[2,4,12]),
 "austin-tx-commission-recommendation":("https://services.austintexas.gov/edims/document.cfm?id=452847",[1,3])
}
MAX_BYTES=8_000_000
class DenyRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("Original government document redirect denied")
def fetch(id):
 url=SOURCES[id][0]
 p=urllib.parse.urlsplit(url)
 if p.scheme!="https" or p.hostname not in {"sanmateo.courts.ca.gov","services.austintexas.gov","www.greenbaywi.gov","www.sanbruno.ca.gov"} or p.netloc!=p.hostname or p.fragment:
  raise ValueError("Untrusted original")
 op=urllib.request.build_opener(DenyRedirect())
 req=urllib.request.Request(url,headers={"User-Agent":"Katoptron-original-government-documents-review/1.0","Accept":"application/pdf"})
 with op.open(req,timeout=25) as res:
  if res.status!=200 or res.geturl()!=url:raise ValueError("Not the exact publisher original")
  body=res.read(MAX_BYTES+1)
 if not 100<len(body)<=MAX_BYTES or not body.startswith(b"%PDF-"):
  raise ValueError("Original is not a bounded PDF")
 return body
def main():
 for id,(url,pages) in SOURCES.items():
  try:
   raw=fetch(id)
   pdf=PdfReader(io.BytesIO(raw),strict=True)
   if pdf.is_encrypted or not 1<=len(pdf.pages)<=120:raise ValueError("Unreadable/too many pages")
   print("ORIGINAL",id,"SHA256",hashlib.sha256(raw).hexdigest(),"PAGES",len(pdf.pages),"BYTES",len(raw),"URL",url)
   for p in pages:
    if p>len(pdf.pages):continue
    t=" ".join((pdf.pages[p-1].extract_text() or "").split())
    # No raw plate data, no full document dumps or private individual records.
    # Preview original text only from public policy, aggregate report,
    # contract order table, oversight findings and resolution documents.
    if id=="green-bay-wi-monthly-2026":
     t=t[:1000]
    elif id=="green-bay-wi-flock-order-2025":
     t=re.sub(r"(?i)(?:[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,})","[public-contact-redacted]",t)
     t=t[:1500]
    else:t=t[:2000]
    print("REVIEW_PAGE",id,p,json.dumps(t,ensure_ascii=False))
  except Exception as e:print("HELD",id,type(e).__name__,str(e)[:125])
 print("PUBLISHED_SUBSTANTIVE_FINDINGS 0")
if __name__=="__main__":main()
