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
    def test_contract_watch_detects_signed_documents_without_claiming_renewal(self):
        signed={"event_key":"signed-2026-01","event_type":"executed_contract",
          "evidence_level":"editorially_verified_signed_agreement",
          "title":"Signed Flock agreement","summary":"Source-dated signed agreement",
          "jurisdiction_label":"Folsom, CA",
          "event_date":"2026-10-20","source_url":"https://gov.example.org/signed"}
        e=S.build_events([signed],[],[],date(2026,10,25))
        self.assertEqual(len(e),1)
        self.assertEqual(e[0]["kind"],"contract_document")
        self.assertTrue(M.eligible("contract_document",{
          "watch_renewals":True,"watch_government":False}))
        self.assertFalse(M.eligible("contract_document",{
          "watch_renewals":False,"watch_government":False}))
        self.assertNotIn("renewal",e[0]["title"].lower())

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
    def test_sender_does_not_replay_prior_events_or_duplicate_delivery(self):
        # Fake all protected DB/API and encrypted SMTP interactions. This
        # tests real delivery orchestration without sending actual messages.
        original=M.api
        receipts=set()
        sent=[]
        subscribers=[{
          "user_id":"test-user-uuid","email":"verified@example.org",
          "locality_key":"folsom|CA",
          "watch_government":True,"watch_vendor":False,
          "watch_sharing":False,"watch_renewals":False,
          "subscribed_at":"2026-10-25T20:00:00Z"
        }]
        records=[
          {"event_key":"before","kind":"government_decision",
           "title":"Historical record","summary":"Historical evidence.",
           "source_url":"https://agency.example.gov/old",
           "source_date":"2026-10-01","evidence_tier":"original_government",
           "observed_at":"2026-10-25T19:00:00Z"},
          {"event_key":"new","kind":"government_decision",
           "title":"New verified government source","summary":"A new published decision.",
           "source_url":"https://agency.example.gov/new",
           "source_date":"2026-10-25","evidence_tier":"original_government",
           "observed_at":"2026-10-25T21:00:00Z"},
          {"event_key":"not-opted","kind":"sharing_list_changed",
           "title":"Secondary sharing observation","summary":"Source reported list changed.",
           "source_url":"https://eyesonflock.com/portal/folsom-ca-pd",
           "source_date":"2026-10-25",
           "evidence_tier":"secondary_aggregated_portal_snapshot",
           "observed_at":"2026-10-25T22:00:00Z"}
        ]
        def fake_api(url,secret,path,method="GET",payload=None):
            if path=="rpc/flock_watch_delivery_candidates":
                return subscribers
            if path.startswith("flock_watch_subscriptions?"):
                return [{"watch_policies":False,"policy_opted_in_at":None}]
            if path.startswith("flock_agency_watch_events?"):
                return records
            if path.startswith("flock_watch_deliveries?") and method=="GET":
                return [{"event_key":x} for x in receipts]
            if path.startswith("flock_watch_deliveries?") and method=="POST":
                receipts.update(row["event_key"] for row in payload)
                return None
            raise AssertionError("Unexpected private Watch request: "+path)
        M.api=fake_api
        try:
            settings=("smtp.example.org",587,"user","secret","alerts@example.org")
            def fake_send(message,connection):
                self.assertEqual(connection,settings)
                self.assertIn("New verified government source",message.get_content())
                self.assertNotIn("Historical record",message.get_content())
                self.assertNotIn("Secondary sharing observation",message.get_content())
                sent.append(message)
            self.assertEqual(M.deliver("https://example.supabase.co","protected",settings,send=fake_send),1)
            self.assertEqual(receipts,{"new"})
            self.assertEqual(len(sent),1)
            self.assertEqual(M.deliver("https://example.supabase.co","protected",settings,send=fake_send),0)
            self.assertEqual(len(sent),1)
            subscribers.clear()  # Actual unsubscribe removes recipient from protected query.
            self.assertEqual(M.deliver("https://example.supabase.co","protected",settings,send=fake_send),0)
        finally:
            M.api=original

    def test_allowlisted_page_reviewed_originals_have_separate_event_kinds(self):
        ledgers=S.load_policy_ledgers()
        events=S.build_policy_events(ledgers)
        self.assertEqual(len(events),5)
        self.assertEqual(len({x["event_key"] for x in events}),5)
        self.assertEqual(sum(x["kind"]=="policy_draft_reviewed" for x in events),2)
        self.assertEqual(sum(x["kind"]=="policy_original_reviewed" for x in events),3)
        self.assertTrue(all(x["evidence_tier"]=="original_government" for x in events))
        self.assertTrue(all(x["source_url"].startswith("https://") for x in events))
        self.assertTrue(all("not" in x["summary"].lower() for x in events))
        green=[x for x in events if x["locality_key"]=="green bay|WI"]
        self.assertEqual(len(green),2)
        self.assertTrue(any(x["kind"]=="policy_draft_reviewed" and x["source_date"] is None for x in green))
        tampered=__import__("copy").deepcopy(ledgers)
        next(x for x in tampered["national"]["documents"]
             if x["id"]=="green-bay-wi-policy-draft-sept-2026")["kind"]="published_department_policy"
        with self.assertRaisesRegex(ValueError,"identity/status"):S.build_policy_events(tampered)
        tampered=__import__("copy").deepcopy(ledgers)
        next(x for x in tampered["riSd"]["documents"]
             if x["id"]=="providence-ri-general-order-35005-sept2026")["original_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"drift"):S.build_policy_events(tampered)

    def test_policy_category_does_not_email_unless_separately_opted_in(self):
        self.assertFalse(M.eligible("policy_original_reviewed",{
          "watch_government":True,"watch_policies":False}))
        self.assertTrue(M.eligible("policy_draft_reviewed",{"watch_policies":True}))
        original=M.api
        events=[
          {"event_key":"old-approved","kind":"policy_original_reviewed",
           "title":"Historical policy indexed","summary":"Old reviewed source",
           "source_url":"https://gov.example.org/policy","source_date":"2026-09-01",
           "evidence_tier":"original_government","observed_at":"2026-10-25T19:00:00Z"},
          {"event_key":"after-category-consent","kind":"policy_draft_reviewed",
           "title":"Unadopted source reviewed","summary":"DRAFT only, no enactment",
           "source_url":"https://gov.example.org/draft","source_date":None,
           "evidence_tier":"original_government","observed_at":"2026-10-25T21:00:00Z"}]
        subscribers=[{
          "user_id":"uuid-test","email":"confirmed@example.org","locality_key":"green bay|WI",
          "watch_government":True,"watch_vendor":False,"watch_sharing":False,
          "watch_renewals":False,"subscribed_at":"2026-10-25T18:00:00Z"}]
        receipts=set();sent=[]
        policy_enabled=False
        def fake_api(url,secret,path,method="GET",payload=None):
            if path=="rpc/flock_watch_delivery_candidates":return subscribers
            if path.startswith("flock_watch_subscriptions?"):
                return [{"watch_policies":policy_enabled,
                         "policy_opted_in_at":"2026-10-25T20:00:00Z" if policy_enabled else None}]
            if path.startswith("flock_agency_watch_events?"):return events
            if path.startswith("flock_watch_deliveries?") and method=="GET":
                return [{"event_key":x} for x in receipts]
            if path.startswith("flock_watch_deliveries?") and method=="POST":
                receipts.update(x["event_key"] for x in payload);return None
            raise AssertionError(path)
        M.api=fake_api
        try:
            settings=("smtp.example.org",587,"user","secret","alerts@example.org")
            def send(msg,settings):
                sent.append(msg.get_content())
            self.assertEqual(M.deliver("https://supabase.example.org","key",settings,send=send),0)
            policy_enabled=True
            self.assertEqual(M.deliver("https://supabase.example.org","key",settings,send=send),1)
            self.assertNotIn("Historical policy indexed",sent[0])
            self.assertIn("Unadopted source reviewed",sent[0])
            self.assertEqual(receipts,{"after-category-consent"})
            self.assertEqual(M.deliver("https://supabase.example.org","key",settings,send=send),0)
        finally:M.api=original

    def test_missing_source_url_cannot_be_alert(self):
        self.assertEqual(S.build_events([{"event_key":"a",
          "event_type":"recorded_legislative_decision",
          "jurisdiction_label":"Folsom, CA","source_url":"http://insecure.example.com",
          "title":"Fake"}],[],[],date(2026,10,25)),[])

if __name__=="__main__":unittest.main()
