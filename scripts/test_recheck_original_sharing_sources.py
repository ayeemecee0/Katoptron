import importlib.util
import urllib.error
import unittest
from pathlib import Path

PATH=Path(__file__).with_name('recheck_original_sharing_sources.py')
spec=importlib.util.spec_from_file_location('primary_share_recheck',PATH)
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


class OriginalSharingCheck(unittest.TestCase):
 def test_gov_html_all_verbatim_names(self):
    html=b'<html><h3>External agencies who EGPD shares Flock ALPR data with</h3><ul><li>Folsom CA PD</li><li>Citrus Heights CA PD</li></ul></html>'
    status,found=M.evaluate(html,'External agencies who EGPD shares Flock ALPR data with',
                  ['Folsom CA PD','Citrus Heights CA PD'])
    self.assertEqual((status,found),('all_previously_published_names_still_present',2))
 def test_missing_list_is_not_revocation(self):
    h=b'<h3>External agencies who EGPD shares Flock ALPR data with</h3><li>Folsom CA PD</li>'
    state,count=M.evaluate(h,'External agencies who EGPD shares Flock ALPR data with',
                           ['Folsom CA PD','Citrus Heights CA PD'])
    self.assertEqual((state,count),('publisher_list_changed_or_incomplete',1))
    state,count=M.evaluate(b'<html><p>No readable list</p></html>','Sharing Network Data With',
                            ['Folsom CA PD'])
    self.assertEqual((state,count),('source_section_unavailable',0))
 def test_missing_source_http_never_revokes(self):
    sources=[{'source_key':'a','source_url':'https://elkgrove.gov/traffic/test',
       'source_section':'External agencies who EGPD shares Flock ALPR data with'}]
    edges=[{'source_key':'a','recipient_label':'Folsom CA PD'}]
    def forbidden(_):
        raise urllib.error.HTTPError('https://elkgrove.gov/traffic/test',403,'Forbidden',None,None)
    rows=M.recheck_sources(sources,edges,forbidden)
    self.assertEqual(rows[0]['check_result'],'source_fetch_unavailable')
    self.assertEqual(rows[0]['source_http_status'],403)
    self.assertEqual(rows[0]['matched_names'],0)
    self.assertNotIn('source_status',rows[0])
 def test_ssrf_blocked(self):
    for url in ('http://elkgrove.gov/test','https://internal.example/snoop',
                'https://elkgrove.gov.evil.example/path','https://user:pass@elkgrove.gov/test'):
        self.assertFalse(M.permitted_url(url))

if __name__=='__main__':unittest.main()
