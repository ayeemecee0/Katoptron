import json
import tempfile
import unittest
from pathlib import Path

import acquire_preverified_legistar_agendas as A

class OriginalGovernmentAcquisitionTests(unittest.TestCase):
    def test_all_verified_seeds_are_exact_agencies_and_publishers(self):
        seeded=A.verified_seed_registry()
        self.assertEqual(set(seeded),set(A.TENANTS))
        self.assertGreaterEqual(len({state for _,state in A.TENANTS.values()}),5)

    def test_alias_or_source_host_tamper_fails_closed(self):
        source=json.loads(A.CATALOG.read_text())
        target=next(r for r in source["sources"]
                    if r["id"]=="cleveland-oh-ordinance-683-2026")
        target["source_url"]="https://bad.example.org/not-a-government-page"
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"seeds.json"
            path.write_text(json.dumps(source))
            with self.assertRaisesRegex(ValueError,"source identity"):
                A.verified_seed_registry(path)
            target["source_url"]="https://cityofcleveland.legistar.com/LegislationDetail.aspx?ID=8042536"
            target["agency"]="Not Cleveland Government"
            path.write_text(json.dumps(source))
            with self.assertRaisesRegex(ValueError,"issuer mismatch"):
                A.verified_seed_registry(path)

    def test_review_queue_dedup_and_no_public_or_watch_changes(self):
        seed={"elpasotexas":"El Paso City Council"}
        docs=[{"url":"https://webapi.legistar.com/v1/elpasotexas/matters/123",
               "headline":"Flock Safety ALPR proposal","publisher":"El Paso City Council",
               "snippet":"Official agenda","status":"unreviewed"}]
        calls=[]
        def collect(tenant,publisher):
            self.assertEqual((tenant,publisher),("elpasotexas","El Paso City Council"))
            return docs
        def queue(lead):
            calls.append(lead)
            return len(calls)==1
        a=A.acquire(seed,collector=collect,enqueue=queue,workers=1)
        b=A.acquire(seed,collector=collect,enqueue=queue,workers=1)
        self.assertEqual(a["new_review_queue_leads"],1)
        self.assertEqual(b["new_review_queue_leads"],0)
        self.assertEqual(len(calls),2)
        self.assertEqual(a["alert_events_created"],0)
        self.assertEqual(a["agencies_with_verified_new_contracts"],0)

    def test_injected_nonlegistar_sources_never_queue(self):
        good={"url":"https://webapi.legistar.com/v1/stpaul/matters/123",
              "publisher":"Saint Paul City Council","status":"unreviewed"}
        for unsafe in [
            dict(good,url="https://example.com/v1/stpaul/matters/123"),
            dict(good,url="https://webapi.legistar.com/v1/other/matters/123"),
            dict(good,status="approved"),
            dict(good,publisher="Different City"),
        ]:
            with self.assertRaises(ValueError):
                A.acquire({"stpaul":"Saint Paul City Council"},
                          collector=lambda *args:[unsafe],
                          enqueue=lambda _:self.fail("Unsafe source queued"),workers=1)

if __name__=="__main__":
    unittest.main()
