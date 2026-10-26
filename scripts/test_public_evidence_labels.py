"""Public copy must never equate source-mapped LPR with certified Flock hardware."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class EvidenceLabels(unittest.TestCase):
    def test_homepage_distinguishes_agency_map_from_manufacturer_certainty(self):
        html=(ROOT/'index.html').read_text(encoding='utf8')
        self.assertIn('Government source-mapped camera positions',html)
        self.assertIn('without individual Flock manufacturer confirmation',html)
        self.assertIn('hardware status may be unknown',html)
    def test_source_attribution_and_original_camera_evidence_remain_distinct(self):
        html=(ROOT/'methodology.html').read_text(encoding='utf8')
        self.assertIn('individual manufacturers are not separately confirmed',html)
        self.assertIn('23 city-police-linked LPR map positions',html)
        self.assertIn('excluded from verified GIS totals',html)
    def test_source_mapped_generic_lpr_excluded_only_from_flock_simulation(self):
        map_js=(ROOT/'map.js').read_text(encoding='utf8')
        compare=(ROOT/'route-comparison.js').read_text(encoding='utf8')
        methodology=(ROOT/'methodology.html').read_text(encoding='utf8')
        self.assertIn('Comparison.eligibleForFlockRoute,signal',map_js)
        self.assertIn('if(!eligible(row))continue', (ROOT/'route-evidence-query.js').read_text(encoding='utf8'))
        self.assertIn('!Comparison.eligibleForFlockRoute(row)',map_js)
        self.assertIn('GENERIC_CITY_LPR_LAYER',compare)
        self.assertIn('source_flock_label_status',map_js)
        self.assertIn("record.source_flock_label_status!=='source_flock_identified'",compare)
        self.assertIn('if(!eligibleForFlockRoute(r))continue',compare)
        self.assertIn('excluded from Flock-only planned-route proximity',methodology)
        self.assertIn('individual device manufacturer is not confirmed',map_js)

    def test_map_popup_remains_qualified(self):
        js=(ROOT/'map.js').read_text(encoding='utf8')
        self.assertIn('actual detections not available',js)
        self.assertIn('camera operation still unknown',js)
        self.assertIn('SOURCE-ATTRIBUTED',js)
        self.assertIn('Excluded from simulations',js)

if __name__=='__main__':
    unittest.main()
