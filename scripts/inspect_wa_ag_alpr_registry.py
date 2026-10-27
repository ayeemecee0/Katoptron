#!/usr/bin/env python3
"""Read-only Washington AGO mandatory ALPR registration index structure audit.
The AGO explicitly says agency registration attestations are *not* verified by
the AGO. The registration records do NOT prove Flock vendor or camera location.
"""
from html.parser import HTMLParser
import json
from scan_national_government_audit_sources import catalog,fetch,PORTALS

class Rows(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.tables=0;self.current_row=None;self.cell=None;self.rows=[]
 def handle_starttag(self,tag,attrs):
  if tag=='table':self.tables+=1
  if tag=='tr':self.current_row=[]
  if tag in ('td','th') and self.current_row is not None:self.cell={'text':'','links':[]}
  if tag=='a' and self.cell is not None:
   href=dict(attrs).get('href','')
   if len(href)<600:self.cell['links'].append(href)
 def handle_data(self,text):
  if self.cell is not None:self.cell['text']=(self.cell['text']+text)[:350]
 def handle_endtag(self,tag):
  if tag in ('td','th') and self.cell is not None and self.current_row is not None:
   self.cell['text']=' '.join(self.cell['text'].split());self.current_row.append(self.cell);self.cell=None
  if tag=='tr' and self.current_row is not None:
   if len(self.current_row)>=2:self.rows.append(self.current_row)
   self.current_row=None

def main():
 sources=catalog(json.loads(PORTALS.read_text()))
 source=next(s for s in sources if s['id']=='wa-ag-public-alpr-agency-registrations')
 data=fetch(source)
 obj=Rows();obj.feed(data.decode('utf-8',errors='replace'))
 print("OFFICIAL_WA_AG_ORIGINAL_TABLES",obj.tables,"ALL_TABULAR_ROWS",len(obj.rows),"BYTES",len(data))
 for idx,row in enumerate(obj.rows[:18]):
  print("PUBLIC_REGISTRATION_ROW",idx,json.dumps(row,ensure_ascii=False)[:1000])
 print("SOURCE_SCOPE_AGENCY_SELF_CERTIFICATION_NOT_AG_ORIGINAL_VERIFICATION")
if __name__=='__main__':main()
