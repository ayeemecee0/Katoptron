import importlib.util,hashlib,unittest
from pathlib import Path
P=Path(__file__).with_name('build_wa_ag_alpr_registry.py')
spec=importlib.util.spec_from_file_location('wa_ag_index',P)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
def fixture(n=20):
 rows=''.join('<tr><td>Public Agency '+str(i)+
 '</td><td>July 6, 2026</td><td><a href="https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/sample'+str(i)+'.pdf?VersionId=PUBLIC'+str(i)+'">click to view</a></td></tr>' for i in range(n))
 return ('<!doctype html><html><body><table><tr><th>Agency Name</th><th>Submitted Date</th><th>Agency Policy</th></tr>'+rows+'</table></body></html>').encode()
class Tests(unittest.TestCase):
 def test_original_agency_self_certifications_do_not_establish_manufacturer(self):
  data=fixture(20);r=M.convert(data,'2026-10-27')
  self.assertEqual(len(r['registrations']),20)
  self.assertEqual(r['source_url'],'https://www.atg.wa.gov/ALPR')
  self.assertEqual(r['source_sha256'],hashlib.sha256(data).hexdigest())
  self.assertTrue(all(x['registry_status'].endswith('not_independently_verified') for x in r['registrations']))
  self.assertTrue(all(x['submitted_on']=='2026-07-06' for x in r['registrations']))
  self.assertTrue(all(len(x['policy_links_from_official_ago_page'])==1 for x in r['registrations']))
  self.assertEqual((r['camera_points_published'],r['flock_vendor_assertions_published'],r['sharing_network_edges_published']),(0,0,0))
 def test_safe_policy_rejects_userinfo_non_public_and_fragments(self):
  self.assertIsNone(M.safe_policy('http://example.com/doc.pdf'))
  self.assertIsNone(M.safe_policy('https://127.0.0.1/private.pdf'))
  self.assertIsNone(M.safe_policy('https://www.atg.wa.gov.evil.test/policy'))
  self.assertIsNone(M.safe_policy('https://a@evil.example/policy'))
  self.assertIsNone(M.safe_policy('javascript:alert(1)'))
  self.assertIsNone(M.safe_policy('https://good.gov/doc#secret'))
  self.assertIsNotNone(M.safe_policy('https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/A%20Policy.pdf?VersionId=HELLO'))
 def test_header_drift_and_duplicate_original_entry_fail_closed(self):
  bad=fixture(20).replace(b'Agency Name',b'License Plate Number')
  with self.assertRaisesRegex(ValueError,'headings'):M.convert(bad,'2026-10-27')
  dup=fixture(20).replace(b'Public Agency 1</td>',b'Public Agency 0</td>')
  with self.assertRaisesRegex(ValueError,'Duplicate'):M.convert(dup,'2026-10-27')
  with self.assertRaisesRegex(ValueError,'table missing'):M.convert(fixture(3),'2026-10-27')
 def test_raw_date_preserved_when_original_format_unknown(self):
  weird=fixture(20).replace(b'July 6, 2026',b'Undated/unclear')
  r=M.convert(weird,'2026-10-27')
  self.assertIsNone(r['registrations'][0]['submitted_on'])
  self.assertEqual(r['registrations'][0]['submitted_date_as_published'],'Undated/unclear')
if __name__=='__main__':unittest.main()
