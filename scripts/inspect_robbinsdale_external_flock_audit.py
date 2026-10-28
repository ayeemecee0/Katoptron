import hashlib,io,json,urllib.request
from pypdf import PdfReader
URL="https://www.lrl.mn.gov/docs/2025/mandated/251675.pdf"
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**kw):raise ValueError("Redirect requires independent verification")
def inspect():
 req=urllib.request.Request(URL,headers={"Accept":"application/pdf"})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=25) as r:
  if r.status!=200 or r.geturl()!=URL:raise ValueError("Original government source changed")
  data=r.read(2_000_001)
 if len(data)>2_000_000 or not data.startswith(b"%PDF-"):raise ValueError("Invalid PDF")
 pdf=PdfReader(io.BytesIO(data),strict=True)
 if pdf.is_encrypted or len(pdf.pages)!=5:raise ValueError("Original audit pagination changed")
 pages=[]
 for i in range(1,5):
  pages.append({"page":i+1,"excerpt":" ".join((pdf.pages[i].extract_text() or "").split())[:1800]})
 return {"url":URL,"sha256":hashlib.sha256(data).hexdigest(),"pages":pages}
if __name__=="__main__":print("ORIGINAL_ROBBINSDALE_AUDIT",json.dumps(inspect()))
