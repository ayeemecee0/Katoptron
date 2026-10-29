import importlib.util
import unittest
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs

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
        claims=set();states={}
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
                return [{"email_enabled":True,"watch_government":True,
                         "watch_vendor":False,"watch_sharing":False,
                         "watch_renewals":False,"watch_policies":False,
                         "policy_opted_in_at":None}]
            if path.startswith("flock_agency_watch_events?"):
                return records
            if path.startswith("flock_watch_send_claims?") and method=="GET":
                return [{"event_key":k,"status":states.get(k,"queued"),
                         "status_changed_at":"2026-10-29T21:00:00Z"} for k in claims]
            if path.startswith("flock_watch_send_claims?") and method=="PATCH":
                q=parse_qs(path.split("?",1)[1])
                key=q["event_key"][0][3:]
                old=q["status"][0][3:]
                if key not in claims or states.get(key)!=old:return []
                states[key]=payload["status"]
                return [{"event_key":key,"status":states[key],
                         "status_changed_at":payload["status_changed_at"]}]
            if path.startswith("flock_watch_send_claims?") and method=="POST":
                event=payload[0]["event_key"]
                if event in claims:return []
                claims.add(event);states[event]="queued";return payload
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

    def test_pre_smtp_claim_prevents_resend_when_receipt_write_fails(self):
        # At-most-once SMTP submission, even if the delivery receipt cannot
        # be written afterwards. The uncertain outcome is held, not replayed.
        original=M.api
        claims=set();states={}
        messages=[]
        now="2026-10-29T21:00:00Z"
        user={"user_id":"confirmed-user","email":"confirmed@example.org",
              "locality_key":"sacramento county|CA",
              "watch_government":True,"watch_vendor":False,
              "watch_sharing":False,"watch_renewals":False,
              "subscribed_at":"2026-10-29T19:50:00Z"}
        event={"event_key":"new-verified-government-event",
               "kind":"government_decision",
               "title":"Newly reviewed government decision",
               "summary":"Official source described a qualifying decision.",
               "source_url":"https://agency.example.gov/council/2026",
               "source_date":"2026-10-29",
               "evidence_tier":"original_government","observed_at":now}
        def fake_api(url,secret,path,method="GET",payload=None):
            if path=="rpc/flock_watch_delivery_candidates":return [user]
            if path.startswith("flock_watch_subscriptions?"):
                return [{"email_enabled":True,"watch_government":True,
                         "watch_vendor":False,"watch_sharing":False,
                         "watch_renewals":False,"watch_policies":False,
                         "policy_opted_in_at":None}]
            if path.startswith("flock_agency_watch_events?"):return [event]
            if path.startswith("flock_watch_deliveries?") and method=="GET":return []
            if path.startswith("flock_watch_send_claims?") and method=="GET":
                return [{"event_key":k,"status":states.get(k,"queued"),
                         "status_changed_at":"2026-10-29T21:00:00Z"} for k in claims]
            if path.startswith("flock_watch_send_claims?") and method=="PATCH":
                q=parse_qs(path.split("?",1)[1])
                key=q["event_key"][0][3:]
                old=q["status"][0][3:]
                if key not in claims or states.get(key)!=old:return []
                states[key]=payload["status"]
                return [{"event_key":key,"status":states[key],
                         "status_changed_at":payload["status_changed_at"]}]
            if path.startswith("flock_watch_send_claims?") and method=="POST":
                key=payload[0]["event_key"]
                if key in claims:return []
                claims.add(key);states[key]="queued";return payload
            if path.startswith("flock_watch_deliveries?") and method=="POST":
                raise RuntimeError("Receipt store unavailable after SMTP handoff")
            raise AssertionError("Unexpected request "+path)
        M.api=fake_api
        settings=("smtp.example.org",587,"user","secret","alerts@example.org")
        try:
            with self.assertRaisesRegex(RuntimeError,"Receipt store unavailable"):
                M.deliver("https://example.supabase.co","key",settings,
                          send=lambda message,_:messages.append(message))
            self.assertEqual(len(messages),1)
            self.assertIn("https://agency.example.gov/council/2026",
                          messages[0].get_content())
            self.assertEqual(M.deliver("https://example.supabase.co","key",settings,
                          send=lambda message,_:messages.append(message)),0)
            self.assertEqual(len(messages),1,"Uncertain submission must not duplicate")
            self.assertEqual(claims,{"new-verified-government-event"})
        finally:M.api=original

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
        receipts=set();claims=set();states={};sent=[]
        policy_enabled=False
        def fake_api(url,secret,path,method="GET",payload=None):
            if path=="rpc/flock_watch_delivery_candidates":return subscribers
            if path.startswith("flock_watch_subscriptions?"):
                return [{"email_enabled":True,"watch_government":True,
                         "watch_vendor":False,"watch_sharing":False,"watch_renewals":False,
                         "watch_policies":policy_enabled,
                         "policy_opted_in_at":"2026-10-25T20:00:00Z" if policy_enabled else None}]
            if path.startswith("flock_agency_watch_events?"):return events
            if path.startswith("flock_watch_send_claims?") and method=="GET":
                return [{"event_key":k,"status":states.get(k,"queued"),
                         "status_changed_at":"2026-10-29T21:00:00Z"} for k in claims]
            if path.startswith("flock_watch_send_claims?") and method=="PATCH":
                q=parse_qs(path.split("?",1)[1])
                key=q["event_key"][0][3:]
                old=q["status"][0][3:]
                if key not in claims or states.get(key)!=old:return []
                states[key]=payload["status"]
                return [{"event_key":key,"status":states[key],
                         "status_changed_at":payload["status_changed_at"]}]
            if path.startswith("flock_watch_send_claims?") and method=="POST":
                event=payload[0]["event_key"]
                if event in claims:return []
                claims.add(event);states[event]="queued";return payload
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

    def test_meaningful_original_government_changes_are_optin_and_source_pinned(self):
        national,okc,apache,adoption=S.load_landmark_sources()
        changes=S.build_landmark_change_events(national,okc,apache,adoption)
        self.assertEqual(len(changes),3)
        self.assertEqual(len({x["event_key"] for x in changes}),3)
        self.assertEqual({x["locality_key"] for x in changes},
            {"moline|IL","oklahoma city|OK","apache junction|AZ"})
        self.assertEqual(sum(x["kind"]=="contract_document" for x in changes),2)
        self.assertEqual(sum(x["kind"]=="government_decision" for x in changes),1)
        self.assertTrue(all(x["source_date"] and x["source_url"].startswith("https://")
                            and x["evidence_tier"]=="original_government" for x in changes))
        contract_only={"watch_government":False,"watch_vendor":False,
                       "watch_renewals":True,"watch_sharing":False}
        self.assertTrue(M.eligible("contract_document",contract_only))
        self.assertFalse(M.eligible("government_decision",contract_only))
        none={"watch_government":False,"watch_vendor":False,
              "watch_renewals":False,"watch_sharing":False}
        self.assertTrue(all(not M.eligible(event["kind"],none) for event in changes))
        import copy
        forged=copy.deepcopy(apache);forged["legal_effective_date_verified"]=True
        with self.assertRaisesRegex(ValueError,"Apache"):
            S.build_landmark_change_events(national,okc,forged,adoption)
        forged=copy.deepcopy(adoption)
        next(x for x in forged["records"] if x["state"]=="AZ")["effective_date"]="2026-10-06"
        with self.assertRaisesRegex(ValueError,"Apache"):
            S.build_landmark_change_events(national,okc,apache,forged)
        forged=copy.deepcopy(national)
        next(x for x in forged["documents"] if x["id"]=="moline-il-signed-pause-2026")["content_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"Moline"):
            S.build_landmark_change_events(forged,okc,apache,adoption)
        forged=copy.deepcopy(okc)
        next(x for x in forged["documents"] if x["id"]=="okc-2026-signed-flock-amendment")["status"]="unsigned_proposal"
        with self.assertRaisesRegex(ValueError,"Oklahoma"):
            S.build_landmark_change_events(national,forged,apache,adoption)

    def test_one_recipient_delivery_diagnostic_never_creates_public_or_private_events(self):
        # Exercises real composition and authorization without connecting to SMTP.
        original=M.api
        confirmed=[{
          "user_id":"test-user-uuid","email":"confirmed@example.org",
          "locality_key":"moline|IL","subscribed_at":"2026-10-29T01:00:00Z"
        }]
        record=[{"email_enabled":True,"watch_government":False,
                 "watch_vendor":False,"watch_sharing":False,
                 "watch_renewals":True,"watch_policies":False}]
        paths=[]
        sent=[]
        def fake_api(url,secret,path,method="GET",payload=None):
            paths.append((path,method))
            if path=="rpc/flock_watch_delivery_candidates":
                self.assertEqual(method,"POST")
                return confirmed
            if path.startswith("flock_watch_subscriptions?"):
                self.assertEqual(method,"GET")
                return record
            raise AssertionError("Diagnostic cannot modify evidence or private receipts")
        M.api=fake_api
        try:
            settings=("smtp.example.org",465,"user","app-password","alerts@example.org")
            def fake_send(message,config):
                self.assertEqual(config,settings)
                self.assertEqual(message["To"],"confirmed@example.org")
                self.assertIn("TEST EMAIL",message["Subject"])
                self.assertIn("NOT a government decision",message.get_content())
                self.assertIn("No public evidence, event",message.get_content())
                self.assertIn("disable your Watch subscription",message.get_content())
                sent.append(message)
            self.assertEqual(M.send_diagnostic("https://example.supabase.co",
                             "protected-key",settings,send=fake_send),1)
            self.assertEqual(len(sent),1)
            self.assertEqual(len(paths),2)
            self.assertTrue(all(not p.startswith("flock_agency_watch_events")
                        and not p.startswith("flock_watch_deliveries")
                        for p,_ in paths))
            confirmed.append(dict(confirmed[0],email="another@example.org"))
            with self.assertRaisesRegex(RuntimeError,"exactly one"):
                M.send_diagnostic("https://example.supabase.co","key",settings,send=fake_send)
            confirmed.pop()
            record[0]["email_enabled"]=False
            with self.assertRaisesRegex(RuntimeError,"active category"):
                M.send_diagnostic("https://example.supabase.co","key",settings,send=fake_send)
            record[0]["email_enabled"]=True
            record[0]["watch_renewals"]=False
            with self.assertRaisesRegex(RuntimeError,"active category"):
                M.send_diagnostic("https://example.supabase.co","key",settings,send=fake_send)
            record[0]["watch_renewals"]=True
            confirmed.clear()
            with self.assertRaisesRegex(RuntimeError,"exactly one"):
                M.send_diagnostic("https://example.supabase.co","key",settings,send=fake_send)
            self.assertEqual(len(sent),1)
        finally:
            M.api=original

    def test_new_source_event_from_real_government_original_is_sent_once_only_to_opt_in(self):
        # End-to-end sender rehearsal with an authenticated original-source
        # document, isolated database stub and stubbed encrypted SMTP. No
        # fabricated production event, recipient, receipt or email is created.
        national,okc,apache,adoption=S.load_landmark_sources()
        originals=S.build_landmark_change_events(national,okc,apache,adoption)
        actual=next(x for x in originals if x["locality_key"]=="apache junction|AZ")
        self.assertEqual(actual["kind"],"government_decision")
        self.assertEqual(actual["evidence_tier"],"original_government")
        self.assertEqual(actual["source_date"],"2026-10-06")
        event=dict(actual,observed_at="2026-10-29T21:01:00Z")
        subscriber=[{"user_id":"test-confirmed-user","email":"test-confirmed@example.org",
            "locality_key":"apache junction|AZ","watch_government":True,
            "watch_vendor":False,"watch_sharing":False,"watch_renewals":False,
            "subscribed_at":"2026-10-29T21:00:00Z"}]
        receipts=set();claims=set();states={};messages=[];orig=M.api
        def fake_api(url,secret,path,method="GET",payload=None):
            if path=="rpc/flock_watch_delivery_candidates":return subscriber
            if path.startswith("flock_watch_subscriptions?"):
                return [{"email_enabled":True,"watch_government":True,
                         "watch_vendor":False,"watch_sharing":False,
                         "watch_renewals":False,"watch_policies":False,
                         "policy_opted_in_at":None}]
            if path.startswith("flock_agency_watch_events?"):return [event]
            if path.startswith("flock_watch_send_claims?") and method=="GET":
                return [{"event_key":k,"status":states.get(k,"queued"),
                         "status_changed_at":"2026-10-29T21:00:00Z"} for k in claims]
            if path.startswith("flock_watch_send_claims?") and method=="PATCH":
                q=parse_qs(path.split("?",1)[1])
                key=q["event_key"][0][3:]
                old=q["status"][0][3:]
                if key not in claims or states.get(key)!=old:return []
                states[key]=payload["status"]
                return [{"event_key":key,"status":states[key],
                         "status_changed_at":payload["status_changed_at"]}]
            if path.startswith("flock_watch_send_claims?") and method=="POST":
                key=payload[0]["event_key"]
                if key in claims:return []
                claims.add(key);states[key]="queued";return payload
            if path.startswith("flock_watch_deliveries?") and method=="GET":
                return [{"event_key":key} for key in receipts]
            if path.startswith("flock_watch_deliveries?") and method=="POST":
                receipts.update(x["event_key"] for x in payload);return None
            raise AssertionError("Unexpected protected API: "+path)
        M.api=fake_api
        settings=("smtp.example.org",465,"sender","secret","alerts@example.org")
        try:
            def send(msg,config):
                self.assertEqual(config,settings)
                self.assertIn("Apache Junction",msg.get_content())
                self.assertIn(event["source_url"],msg.get_content())
                self.assertNotIn("TEST EMAIL",msg["Subject"])
                messages.append(msg)
            self.assertEqual(M.deliver("https://example.supabase.co",
                         "protected",settings,send=send),1)
            self.assertEqual(receipts,{event["event_key"]})
            self.assertEqual(M.deliver("https://example.supabase.co",
                         "protected",settings,send=send),0)
            subscriber.clear()  # actual unsubscribe excludes account from recipient RPC
            self.assertEqual(M.deliver("https://example.supabase.co",
                         "protected",settings,send=send),0)
            self.assertEqual(len(messages),1)
        finally:M.api=orig

    def test_missing_source_url_cannot_be_alert(self):
        self.assertEqual(S.build_events([{"event_key":"a",
          "event_type":"recorded_legislative_decision",
          "jurisdiction_label":"Folsom, CA","source_url":"http://insecure.example.com",
          "title":"Fake"}],[],[],date(2026,10,25)),[])

if __name__=="__main__":unittest.main()
