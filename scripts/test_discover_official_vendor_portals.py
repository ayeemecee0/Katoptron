"""A direct government Flock portal hyperlink is private research only."""
import unittest
from unittest.mock import patch
from discover_government_gis_links import Anchors
import discover_official_vendor_portals as d

PAGE='https://police.city.example.gov/flock'
PORTAL='https://transparency.flocksafety.com/city-example-pd'

def doc(body):
    result=Anchors()
    result.feed(body)
    return result

class VendorLinkResearch(unittest.TestCase):
    def test_exact_vendor_link_under_original_agency_evidence(self):
        page=doc('<h1>Flock Safety ALPR cameras used by City Police</h1>'
                 '<a href="'+PORTAL+'">Police transparency statistics</a>')
        records=d.direct_vendor_portals(page,PAGE,'a'*64)
        self.assertEqual(len(records),1)
        self.assertEqual(records[0]['portal_url'],PORTAL)
        self.assertEqual(records[0]['government_source_url'],PAGE)

    def test_link_text_is_not_original_camera_disclosure(self):
        page=doc('<h2>Police links</h2><a href="'+PORTAL+'">Flock cameras</a>')
        self.assertEqual(d.direct_vendor_portals(page,PAGE,'a'*64),[])

    def test_vendor_hostname_and_path_pinned(self):
        for url in (
          'https://transparency.flocksafety.com.evil.example/demo',
          'http://transparency.flocksafety.com/demo',
          'https://transparency.flocksafety.com/admin/anything',
          'https://transparency.flocksafety.com/demo?api_key=not_allowed',
          'https://transparency.flocksafety.com/demo#frag',
          'https://attacker.example/flock',
        ):
            self.assertIsNone(d.portal_url(url),url)
        self.assertEqual(d.portal_url(PORTAL),PORTAL)

    def test_matching_repeat_is_idempotent(self):
        item={'government_source_url':PAGE,'portal_url':PORTAL,
              'government_page_sha256':'a'*64}
        with patch.object(d,'api_request',return_value=[dict(item)]) as api:
            self.assertFalse(d.stage(item))
        self.assertEqual(api.call_count,1)

    def test_changed_source_receipt_is_held_no_write(self):
        item={'government_source_url':PAGE,'portal_url':PORTAL,
              'government_page_sha256':'a'*64}
        with patch.object(d,'api_request',return_value=[{
            **item,'government_page_sha256':'b'*64
        }]) as api:
            with self.assertRaisesRegex(ValueError,'changed'):
                d.stage(item)
        self.assertEqual(api.call_count,1)

    def test_new_leads_write_private_queue_only(self):
        item={'government_source_url':PAGE,'portal_url':PORTAL,
              'government_page_sha256':'a'*64}
        with patch.object(d,'api_request',side_effect=[[],None]) as api:
            self.assertTrue(d.stage(item))
        self.assertIn('flock_vendor_portal_source_leads',api.call_args.args[0])
        self.assertNotIn('flock_vendor_portal_snapshots',api.call_args.args[0])
        self.assertNotIn('flock_camera_locations',api.call_args.args[0])

    def test_dry_run_does_not_write(self):
        page=doc('<h2>Flock Safety ALPR cameras</h2>'
                 '<a href="'+PORTAL+'">Flock portal</a>')
        with patch.object(d,'fetch_government_page',return_value=(page,'a'*64)):
            with patch.object(d,'stage') as write:
                r=d.scan(dry_run=True,pages=[PAGE])
        write.assert_not_called()
        self.assertEqual(r['direct_vendor_portal_links'],1)

if __name__=='__main__':
    unittest.main()
