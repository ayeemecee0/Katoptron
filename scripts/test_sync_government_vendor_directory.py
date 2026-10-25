import unittest
from unittest.mock import Mock,patch
from discover_government_gis_links import Anchors
import sync_government_vendor_directory as s

PROGRAM={'program_key':'springfield','official_evidence_url':'https://springfield.gov/flock'}
PORTAL='https://transparency.flocksafety.com/springfield-police'

def page(links=True):
    doc=Anchors()
    html='<h1>Flock Safety automatic license plate cameras</h1>'
    if links:html+='<a href="'+PORTAL+'">Transparency report</a>'
    doc.feed(html)
    return doc,'a'*64

class GovernmentVendorLinks(unittest.TestCase):
    def test_first_party_direct_link_visible_only_as_directory(self):
        calls=[]
        def api(path,method='GET',payload=None,prefer=None):
            calls.append((path,method,payload))
            return [] if method=='GET' else None
        self.assertEqual(s.inspect(PROGRAM,api,lambda _:page()),1)
        self.assertEqual(len(calls),2)
        self.assertIn('flock_government_vendor_directory?',calls[1][0])
        self.assertEqual(calls[1][2][0]['link_status'],'direct_government_link')
        self.assertFalse(any('camera_locations' in x[0] for x in calls))

    def test_revokes_removed_original_link_without_guessing_absence_on_failure(self):
        calls=[]
        def api(path,method='GET',payload=None,prefer=None):
            calls.append((path,method,payload))
            return [{'portal_url':PORTAL}] if method=='GET' else None
        self.assertEqual(s.inspect(PROGRAM,api,lambda _:page(False)),0)
        self.assertEqual(calls[-1][1],'PATCH')
        self.assertEqual(calls[-1][2]['link_status'],'withdrawn')

    def test_original_page_unavailable_does_not_change_directory(self):
        api=Mock()
        with self.assertRaises(OSError):
            s.inspect(PROGRAM,api,lambda _: (_ for _ in ()).throw(OSError()))
        api.assert_not_called()

if __name__=='__main__':unittest.main()
