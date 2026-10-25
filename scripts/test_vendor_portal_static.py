"""Public Flock snapshot UI never treats portal camera totals as map pins."""
import pathlib
import re
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class VendorPortalStaticTests(unittest.TestCase):
    def setUp(self):
        self.page=(ROOT/'portals.html').read_text(encoding='utf-8')

    def test_public_page_uses_immutable_source_snapshots(self):
        self.assertIn('flock_vendor_portal_snapshots',self.page)
        self.assertIn('eq.verified_source_snapshot',self.page)
        self.assertIn('reported_total_cameras',self.page)
        self.assertIn('camera_count_scope', (ROOT/'supabase/migrations/088_vendor_first_party_portal_snapshots.sql').read_text())
        self.assertIn('not a count of verified individual ALPR map pins',self.page)
        self.assertNotIn('flock_camera_locations?',self.page)
        self.assertNotIn('innerHTML',self.page)

    def test_original_url_is_restricted_to_vendor_host(self):
        self.assertIn("u.hostname==='transparency.flocksafety.com'",self.page)
        self.assertIn("u.protocol==='https:'",self.page)
        self.assertIn("link.rel='noopener noreferrer'",self.page)

    def test_inline_javascript_parses(self):
        block=re.search(r'<script>\s*([\s\S]*?)\s*</script>',self.page)
        self.assertIsNotNone(block)
        with tempfile.NamedTemporaryFile('w',suffix='.js',encoding='utf-8') as f:
            f.write(block.group(1))
            f.flush()
            result=subprocess.run(['node','--check',f.name],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)

if __name__=='__main__':
    unittest.main()
