import importlib.util
import unittest
from datetime import date
from pathlib import Path

def load(stem):
    path=Path(__file__).with_name(stem+".py")
    spec=importlib.util.spec_from_file_location(stem,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

S=load("sync_agency_watch_events")
M=load("send_government_watch_alerts")

class GovernmentWatchSafety(unittest.TestCase):
    def test_source_events_are_narrow_dated_not_plate_reads(self):
        govt=[
          {"event_key":"decision-1","event_type":"recorded_legislative_decision",
           "evidence_level":"verified_governing_body_action","title":"County action",
           "summary":"Council vote source available","jurisdiction_label":"Folsom, CA",
           "event_date":"2026-10-18","source_url":"https://gov.example.org/action"},
          {"event_key":"agenda-1","event_type":"agenda_mention",
           "jurisdiction_label":"Folsom, CA",
           "source_url":"https://gov.example.org/agenda"}]
        portal=[
          {"agency_key":"folsom_ca_pd","agency_label":"Folsom CA PD",
           "source_date":"2026-08-10","retention_days":30,
           "disclosure_status":"verified_source_snapshot",
           "portal_url":"https://transparency.flocksafety.com/folsom-ca-pd"},
          {"agency_key":"folsom_ca_pd","agency_label":"Folsom CA PD",
           "source_date":"2026-10-20","retention_days":7,
           "disclosure_status":"verified_source_snapshot",
           "portal_url":"https://transparency.flocksafety.com/folsom-ca-pd"}]
        contracts=[{"contract_key":"real-signed-1","jurisdiction_label":"Folsom, CA",
                    "ends_on":"2026-11-20","source_url":"https://gov.example.org/signed"}]
        a=S.build_events(govt,portal,contracts,date(2026,10,25))
        kinds=[x["kind"] for x in a]
        self.assertEqual(kinds.count("government_decision"),1)
        self.assertEqual(kinds.count("vendor_portal_snapshot"),2)
        self.assertEqual(kinds.count("retention_changed"),1)
        self.assertEqual(kinds.count("contract_renewal"),1)
        self.assertTrue(all(x["locality_key"]=="folsom|CA" for x in a))
        self.assertTrue(all(x["source_url"].startswith("https://") for x in a))
        self.assertNotIn("agenda_mention",str(a))
        self.assertIn("NOT proof",str(a))
    def test_sharing_alerts_require_actual_explicit_optin(self):
        account={"watch_government":True,"watch_vendor":False,
          "watch_sharing":False,"watch_renewals":False}
        self.assertTrue(M.eligible("government_decision",account))
        for other in ("sharing_list_changed","retention_changed",
                      "vendor_portal_snapshot","contract_renewal"):
            self.assertFalse(M.eligible(other,account))
    def test_confirmed_sender_compose_never_mentions_plates_or_tracks_route(self):
        mail=M.make_email("confirmed@example.org","folsom|CA",[
          {"title":"City source record","summary":"Original council decision.",
            "evidence_tier":"original_government",
            "source_date":"2026-10-20","source_url":"https://gov.example.org/a"}],
          "alerts@katoptron.example.org")
        self.assertEqual(mail["To"],"confirmed@example.org")
        self.assertIn("Manage or disable",mail.get_content())
        self.assertIn("not a travel route",mail.get_content())
        with self.assertRaisesRegex(ValueError,"Timezone"):
            M.iso_datetime("2026-10-25T10:00:00")
    def test_missing_source_url_cannot_be_alert(self):
        self.assertEqual(S.build_events([{"event_key":"a",
          "event_type":"recorded_legislative_decision",
          "jurisdiction_label":"Folsom, CA","source_url":"http://insecure.example.com",
          "title":"Fake"}],[],[],date(2026,10,25)),[])

if __name__=="__main__":unittest.main()
