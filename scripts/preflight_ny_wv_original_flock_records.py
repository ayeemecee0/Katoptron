#!/usr/bin/env python3
"""Byte-level preflight of NY county's historical Flock decisions and WV oversight.

Original county government publication is a city/county self-report. State
legislature committee coverage is evidence of a hearing, not a statute,
agency deployment or vendor access. No plate/read/individual-record data.
"""
import hashlib,html.parser,io,json,re,urllib.request
from pypdf import PdfReader
SOURCES={
 "ny-tompkins-sheriff-july2025-report":{
  "state":"NY","type":"pdf","bytes_max":2_000_000,
  "source_url":"https://www.tompkinscountyny.gov/files/assets/county/v/1/sheriffs-office/documents/public-safety-meeting-reports/public-safety-meeting-report-july-2025.pdf",
  "pdf_page":7,"needle":["July 2025","Flock Safety","National Search"]},
 "ny-tompkins-april2026-termination":{
  "state":"NY","type":"html","bytes_max":1_100_000,
  "source_url":"https://www.tompkinscountyny.gov/News-articles/Highlights-of-the-4726-regular-and-41426-special-Tompkins-County-Legislature-meetings",
  "needle":["April 14","Flock Group","12-1","May 28"]},
 "wv-august2026-legislature-flock-hearing":{
  "state":"WV","type":"html","bytes_max":700_000,
  "source_url":"https://blog.wvlegislature.gov/headline/2026/08/10/interim-report-joint-committee-on-government-organization/",
  "needle":["August 10, 2026","Flock","Committee","2027"]},
 "wv-august2026-official-agenda":{
  "state":"WV","type":"html","bytes_max":450_000,
  "source_url":"https://www.wvlegislature.gov/Committees/Interims/agenda.cfm?abb=GOVORG&recordid=5649",
  "needle":["August 9, 2026","Flock","Institute for Justice"]}
}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("original_gov_redirect")
class Text(html.parser.HTMLParser):
 def __init__(self):super().__init__();self.words=[];self.skip=[]
 def handle_starttag(self,tag,attrs):
  if tag in ("script","style","svg","noscript"):self.skip.append(tag)
 def handle_endtag(self,tag):
  if tag in self.skip:self.skip.remove(tag)
 def handle_data(self,t):
  if not self.skip:self.words.append(t)
def retrieve(key):
 if key not in SOURCES:raise ValueError("Unapproved government source")
 row=SOURCES[key];url=row["source_url"]
 req=urllib.request.Request(url,headers={"Accept":"text/html,application/pdf",
  "User-Agent":"Katoptron-original-NY-WV-government-program-review/1.0"})
 try:
  with urllib.request.build_opener(NoRedirect()).open(req,timeout=28) as r:
   if r.status!=200 or r.geturl()!=url:raise ValueError("Original government URL changed")
   data=r.read(row["bytes_max"]+1)
 except urllib.error.HTTPError as e:
  raise ValueError("gov_http_"+str(e.code)) from None
 if not 100<len(data)<=row["bytes_max"]:raise ValueError("Unbounded/empty government original")
 return data
def inspect(key,b):
 row=SOURCES[key]
 if not isinstance(b,bytes) or len(b)>row["bytes_max"]:raise ValueError("Invalid byte buffer")
 if row["type"]=="pdf":
  if not b.startswith(b"%PDF-"):raise ValueError("PDF original changed format")
  pdf=PdfReader(io.BytesIO(b),strict=True)
  if pdf.is_encrypted or not 1<=len(pdf.pages)<=30:raise ValueError("Unreadable government PDF")
  if row["pdf_page"]>len(pdf.pages):raise ValueError("Referenced original report page missing")
  text=" ".join((pdf.pages[row["pdf_page"]-1].extract_text() or "").split())
  pages=len(pdf.pages)
 else:
  if b"<html" not in b[:1700].lower() and b"<!doctype" not in b[:1700].lower():raise ValueError("Government HTML changed format")
  parser=Text();parser.feed(b.decode("utf8",errors="replace"))
  text=" ".join(" ".join(parser.words).split())
  pages=None
 missing=[word for word in row["needle"] if word.casefold() not in text.casefold()]
 if missing:raise ValueError("Government original source substantive anchors missing: "+",".join(missing))
 return {"source_id":key,"state":row["state"],"status":"original_government_source_retrieved_needs_individual_page_review",
  "sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),"pages":pages,
  "source_type":row["type"],"policy_adopted":False,"equipment_current":False,
  "new_camera_coordinates":False}
def main():
 rows=[]
 for k in SOURCES:
  try:rows.append(inspect(k,retrieve(k)))
  except Exception as e:rows.append({"source_id":k,"state":SOURCES[k]["state"],
    "status":"held_original_government_source","error_type":type(e).__name__,
    "reason":str(e)[:150],"policy_adopted":False,"equipment_current":False,
    "new_camera_coordinates":False})
 for r in rows:print("NY_WV_PRIMARY_GOVERNMENT_PREFLIGHT",json.dumps(r,sort_keys=True))
 print("NY_WV_ORIGINAL_COUNTS",json.dumps({"originals":len(rows),
  "accessible":sum(x["status"].startswith("original_government") for x in rows),
  "held":sum(x["status"].startswith("held_") for x in rows),"new_verified_camera_locations":0},sort_keys=True))
if __name__=="__main__":main()
