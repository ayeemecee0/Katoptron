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
        known,files=A.indexed_matters()
        self.assertEqual(set(known),set(A.TENANTS))
        self.assertTrue(all(known[k] for k in known))
        self.assertEqual(set(files),set(A.TENANTS))
        self.assertTrue(all(files[k] for k in files))

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
        guid="5C72F308-9FAC-49FA-A468-F0FF71E2A4A1"
        def detail(_):
            return {"MatterId":123,"MatterGuid":guid,"MatterFile":"ZZ-123","MatterRestrictViewViaWeb":False}
        known={"elpasotexas":set()}
        a=A.acquire(seed,collector=collect,enqueue=queue,workers=1,
                    known_guids=known,known_file_ids={"elpasotexas":set()},detail_fetch=detail)
        b=A.acquire(seed,collector=collect,enqueue=queue,workers=1,
                    known_guids=known,known_file_ids={"elpasotexas":set()},detail_fetch=detail)
        self.assertEqual(a["new_review_queue_leads"],1)
        self.assertEqual(b["new_review_queue_leads"],0)
        self.assertEqual(len(calls),2)
        self.assertEqual(a["alert_events_created"],0)
        self.assertEqual(a["agencies_with_verified_new_contracts"],0)

    def test_already_page_reviewed_guid_is_excluded_even_with_different_id_url(self):
        known,files=A.indexed_matters()
        reviewed=next(iter(known["elpasotexas"]))
        seed={"elpasotexas":"El Paso City Council"}
        original=[{"url":"https://webapi.legistar.com/v1/elpasotexas/matters/16407",
          "headline":"Council motion on ALPR contracting","publisher":"El Paso City Council",
          "status":"unreviewed"}]
        result=A.acquire(seed,collector=lambda *_:original,
                         enqueue=lambda _: self.fail("Reviewed GUID must never be requeued"),
                         workers=1,known_guids=known,known_file_ids=files,
                         detail_fetch=lambda _:{"MatterId":16407,"MatterGuid":reviewed,
                          "MatterFile":"ZZ-16407"})
        self.assertEqual(result["candidate_matches"],1)
        self.assertEqual(result["already_in_source_catalog"],1)
        self.assertEqual(result["new_uncatalogued_matches"],0)
        self.assertEqual(result["new_review_queue_leads"],0)
        self.assertEqual(result["alert_events_created"],0)

    def test_mismatched_api_guid_but_identical_official_file_number_is_not_new(self):
        known,files=A.indexed_matters()
        seed={"elpasotexas":"El Paso City Council"}
        lead=[{"url":"https://webapi.legistar.com/v1/elpasotexas/matters/16407",
          "publisher":"El Paso City Council","status":"unreviewed"}]
        result=A.acquire(seed,collector=lambda *_:lead,known_guids=known,
             known_file_ids=files,
             detail_fetch=lambda _:{"MatterId":16407,
                 "MatterGuid":"D912B783-56A8-4549-8586-42EC6CE50246",
                 "MatterFile":"26-1092"},
             enqueue=lambda _:self.fail("Already indexed File # must be held"),
             workers=1)
        self.assertEqual(result["already_in_source_catalog"],1)
        self.assertEqual(result["new_uncatalogued_matches"],0)
        self.assertEqual(result["new_review_queue_leads"],0)

    def test_missing_or_disagreeing_matter_guid_is_held_not_assumed_novel(self):
        seed={"stpaul":"Saint Paul City Council"}
        lead={"url":"https://webapi.legistar.com/v1/stpaul/matters/345",
              "publisher":"Saint Paul City Council","status":"unreviewed"}
        for payload in [
            {"MatterId":345},
            {"MatterId":100,"MatterGuid":"C3E85809-F081-4898-8CE1-B1DB7B412C78"},
            {"MatterId":345,"MatterGuid":"not-a-guid"},
            {"MatterId":345,"MatterGuid":"C3E85809-F081-4898-8CE1-B1DB7B412C78",
             "MatterRestrictViewViaWeb":True}
        ]:
            result=A.acquire(seed,collector=lambda *_:[lead],known_guids={"stpaul":set()},
                         detail_fetch=lambda _:payload,workers=1,
                         known_file_ids={"stpaul":set()},
                         enqueue=lambda _:self.fail("Unverifiable GUID must never queue"))
            self.assertEqual(result["unreconciled_guid_hold"],1)
            self.assertEqual(result["new_review_queue_leads"],0)

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
                          enqueue=lambda _:self.fail("Unsafe source queued"),workers=1,
                          known_guids={"stpaul":set()},known_file_ids={"stpaul":set()},
                          detail_fetch=lambda *_: self.fail("Unsafe detail queried"))

if __name__=="__main__":
    unittest.main()
