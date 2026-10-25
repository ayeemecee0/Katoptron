"""Offline no-network Peoria overlap safety tests."""
import unittest
from probe_peoria_overlap import summarize


class PeoriaOverlapTests(unittest.TestCase):
    def test_distinct_and_nearby_aggregates(self):
        source = [(33.5, -112.25), (33.6, -112.20)]
        canonical = [{'latitude': 33.5001, 'longitude': -112.2501}]
        result = summarize(source, canonical)
        self.assertEqual(result, {'source_points': 2,
                                 'possible_existing_nearby': 1,
                                 'no_existing_within_100m': 1})

    def test_missing_canonical_geometry_held(self):
        with self.assertRaisesRegex(ValueError, 'invalid geometry'):
            summarize([(33.5, -112.25)], [{'latitude': None, 'longitude': 1}])

    def test_empty_source_held(self):
        with self.assertRaisesRegex(ValueError, 'empty'):
            summarize([], [])


if __name__ == '__main__':
    unittest.main()
