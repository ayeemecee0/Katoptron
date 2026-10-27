import importlib.util
import hashlib
import io
import json
from pathlib import Path
import unittest

SCRIPT=Path(__file__).with_name('scan_national_government_audit_sources.py')
spec=importlib.util.spec_from_file_location('government_source_watch',SCRIPT)
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
PORTALS=json.loads(M.PORTALS.read_text(encoding='utf-8'))
SOURCES=M.catalog(PORTALS)

class Reader:
 def __init__(self,*args,**kwargs):
  self.is_encrypted=False
  self.pages=[object() for _ in range(10)]

class TestNationalPublisherWatch(unittest.TestCase):
 def test_curated_government_domains_are_exact_and_multistate(self):
  self.assertEqual(len(SOURCES),14)
  self.assertEqual({s['state'] for s in SOURCES},{'CA','WI','OR','TX','VA','DE','IL','WA'})
  self.assertEqual(sum(s['kind']=='pdf_original' for s in SOURCES),3)
  for source in SOURCES:self.assertTrue(M.canonical(source['url'],set(source['allowed_document_hosts'])))
  self.assertFalse(M.canonical('https://www.sanbruno.ca.gov.evil.example/a',{'www.sanbruno.ca.gov'}))
  self.assertFalse(M.canonical('https://www.sanbruno.ca.gov@evil.example/a',{'www.sanbruno.ca.gov'}))
  self.assertFalse(M.canonical('http://www.sanbruno.ca.gov/a',{'www.sanbruno.ca.gov'}))
  self.assertFalse(M.canonical('https://www.sanbruno.ca.gov/a#page=2',{'www.sanbruno.ca.gov'}))
  self.assertFalse(M.canonical('https://www.sanbruno.ca.gov/a?raw=1',{'www.sanbruno.ca.gov'}))
  self.assertEqual(M.canonical('https://services.austintexas.gov/edims/document.cfm?id=452710',
     {'services.austintexas.gov'}),'https://services.austintexas.gov/edims/document.cfm?id=452710')
  self.assertFalse(M.canonical('https://services.austintexas.gov/edims/document.cfm?id=12&private=1',
     {'services.austintexas.gov'}))
 def test_source_registry_poisoning_fails_closed(self):
  sample=PORTALS['sources'][0]
  for value in [{**sample,'url':'https://evil.example/doc'},
   {**sample,'allowed_document_hosts':['evil.example']},
   {**sample,'publisher_role':'independently_proven_current_cameras'},
   {**sample,'state':'NY'}]:
   with self.assertRaises(ValueError):M.catalog({'schema_version':1,'sources':[value]})
  with self.assertRaises(ValueError):M.catalog({'schema_version':1,'sources':[sample,sample]})
 def test_austin_adjacent_backup_labels_and_no_personal_logs(self):
  source=next(x for x in SOURCES if x['id']=='tx-austin-public-safety-audits')
  html='''<!doctype html><html><body>
  <a href="https://services.austintexas.gov/edims/document.cfm?id=452710">Backup</a> - Item #5 APD License Plate Reader Audit Report - May 2025
  <a href="https://services.austintexas.gov/edims/document.cfm?id=452711">Backup</a> - Item #6 Raw ALPR Search Logs
  <a href="https://evil.example/records">APD License Plate Reader Audit</a>
  <a href="https://services.austintexas.gov/edims/document.cfm?id=452710">Backup</a> - Item #5 APD License Plate Reader Audit Report
  <a href="https://services.austintexas.gov/edims/document.cfm?id=452712">Budget spreadsheet</a>
  </body></html>'''
  results=M.candidates(source,html)
  self.assertEqual(len(results),1)
  self.assertEqual(results[0]['candidate_type'],'original_audit_or_oversight_candidate')
  self.assertEqual(results[0]['source_url'],'https://services.austintexas.gov/edims/document.cfm?id=452710')
  self.assertEqual(results[0]['status'],'official_publisher_link_metadata_only_not_source_content_reviewed')
  self.assertNotIn('plate numbers',str(results))
 def test_mixed_sources_do_not_promote_original_pdf_facts(self):
  original=next(x for x in SOURCES if x['kind']=='pdf_original')
  html_source=next(x for x in SOURCES if x['id']=='ca-san-bruno-alpr-audits')
  payload=b'%PDF-1.7\n'+b'x'*200
  html=b'<!doctype html><html><body><a href="/DocumentCenter/View/9280/SBPD-Flock-ALPR-Annual-Audit---2025">SBPD Flock 2025 annual audit</a></body></html>'
  record=M.run([original,html_source],fetcher=lambda r:payload if r['kind']=='pdf_original' else html,reader=Reader)
  self.assertEqual(record['government_publishers_monitored'],2)
  self.assertEqual(record['states_monitored'],2)
  self.assertEqual(len(record['original_pdf_receipts']),1)
  self.assertEqual(record['original_pdf_receipts'][0]['sha256'],hashlib.sha256(payload).hexdigest())
  self.assertEqual(len(record['linked_candidates']),1)
  self.assertEqual(record['substantive_facts_auto_published'],0)
  self.assertEqual(record['camera_locations_auto_published'],0)
  self.assertEqual(record['sharing_edges_auto_published'],0)
 def test_unreviewed_links_rank_before_existing_curated_originals(self):
  source=next(x for x in SOURCES if x['id']=='ca-san-bruno-alpr-audits')
  reviewed_url='https://www.sanbruno.ca.gov/DocumentCenter/View/9280/SBPD-Flock-ALPR-Annual-Audit---2025'
  new_url='https://www.sanbruno.ca.gov/DocumentCenter/View/99999/Novel-Flock-ALPR-Audit-2026'
  html=f'<html><body><a href="{reviewed_url}">SBPD Flock Audit 2025</a><a href="{new_url}">SBPD Flock 2026 audit</a></body></html>'.encode()
  outcome=M.run([source],fetcher=lambda _:html,reviewed={reviewed_url})
  self.assertEqual(outcome['unreviewed_original_link_candidates'],1)
  self.assertEqual(outcome['already_reviewed_original_links'],1)
  self.assertEqual(outcome['linked_candidates'][0]['source_url'],new_url)
  self.assertEqual(outcome['linked_candidates'][0]['review_status'],'new_original_link_needs_individual_content_review')
  self.assertEqual(outcome['linked_candidates'][1]['review_status'],'already_individually_page_reviewed_with_pinned_original')
 def test_unavailable_source_not_silently_recast_as_withdrawal(self):
  source=SOURCES[0]
  def err(_):raise TimeoutError('government site busy')
  result=M.run([source],fetcher=err)
  self.assertEqual(result['source_checks'][0]['status'],'official_source_unavailable_needs_recheck')
  self.assertEqual(result['source_checks'][0]['error_type'],'TimeoutError')
  self.assertNotIn('government site busy',str(result))
 def test_pdf_no_raw_contents_are_retained(self):
  source=next(x for x in SOURCES if x['kind']=='pdf_original')
  raw=b'%PDF-1.7\n'+b'ABC'*50
  record=M.receipt(source,raw,Reader)
  self.assertEqual(record['pages'],10)
  self.assertEqual(record['status'],'machine_original_pdf_receipt_no_content_claims')
  self.assertNotIn('text',record)
  self.assertNotIn('findings',record)
  with self.assertRaises(ValueError):M.receipt(source,b'definitely not pdf',Reader)

if __name__=='__main__':unittest.main()
