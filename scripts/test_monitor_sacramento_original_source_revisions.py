"""Sacramento original publisher revision-watch security and lifecycle regressions."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("sacramento_original_monitor",HERE/"monitor_sacramento_original_source_revisions.py")
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

class SacramentoOriginalWatchTests(unittest.TestCase):
    def test_three_pinned_sources_with_no_untrusted_hosts(self):
        docs=M.validated_sources()
        self.assertEqual(len(docs),3)
        self.assertEqual({x["id"] for x in docs},set(M.TRUSTED))
        clone=json.loads(M.CATALOG.read_text())
        clone["sources"][0]["url"]="https://example.com/government.pdf"
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"invalid.json";path.write_text(json.dumps(clone))
            with self.assertRaisesRegex(ValueError,"Source URL"):
                M.validated_sources(path)

    def test_substantive_html_body_hash_ignores_markup_but_changes_on_content_edit(self):
        doc={"mode":"html","start_anchor":"I. Policy Statement",
             "end_anchor":"Sacramento District Attorney's Office",
             "required_phrase":"Automated License Plate Reader"}
        substance=("The Automated License Plate Reader database is accessed only for "
                   "documented legitimate investigations. Internal access requires "
                   "authorization and review by designated management. ")*4
        a=("<html><head><style>IGNORED</style></head><body><h2>I. Policy Statement</h2>"
           "<div>"+substance+"</div><p>Sacramento District Attorney's Office</p>"
           "<script>DO NOT INDEX</script></body></html>").encode()
        b=("<html><body>I. Policy Statement <p>"+substance+"</p>"
           "Sacramento District Attorney's Office</body></html>").encode()
        self.assertEqual(M.fingerprint(doc,a),M.fingerprint(doc,b))
        changed=b.replace(b"requires ",b"also requires ")
        self.assertNotEqual(M.fingerprint(doc,a),M.fingerprint(doc,changed))
        with self.assertRaisesRegex(ValueError,"topic phrase absent"):
            M.fingerprint(doc,b.replace(b"Automated License Plate Reader",b"Generic database elsewhere"))
        with self.assertRaisesRegex(ValueError,"heading missing"):
            M.fingerprint(doc,b.replace(b"I. Policy Statement",b"Missing Statement"))

    def test_pdf_bytes_require_actual_pdf_header_and_eof(self):
        doc={"mode":"pdf"}
        good=b"%PDF-1.6\n"+b"x"*1200+b"\n%%EOF"
        self.assertEqual(M.fingerprint(doc,good),hashlib.sha256(good).hexdigest())
        for bad in [b"x"*1400,b"%PDF-1.6\n"+b"x"*1400,b"%PDF-1.6\n"+b"x"*100+b"%%EOF"]:
            with self.assertRaisesRegex(ValueError,"intact source PDF"):
                M.fingerprint(doc,bad)

    def test_off_publisher_redirect_is_held(self):
        class FakeReply:
            def __init__(self,url):self.url=url
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def geturl(self):return self.url
            def read(self,*args):return b"x"*2500
        doc={"url":"https://www.sacda.org/policies/alpr/","mode":"pdf"}
        with self.assertRaisesRegex(ValueError,"left verified publisher"):
            M.safe_response(doc,request=lambda req,timeout:FakeReply("https://example.net/private"))
        with self.assertRaisesRegex(ValueError,"intact source PDF"):
            M.safe_response(doc,request=lambda req,timeout:FakeReply(doc["url"]))

    def test_first_observation_is_baseline_not_event(self):
        observed={key:hashlib.sha256(key.encode()).hexdigest() for key in M.TRUSTED}
        state,first,changes=M.compare({},observed)
        self.assertEqual(state,observed)
        self.assertEqual(set(first),set(M.TRUSTED))
        self.assertEqual(changes,[])
        self.assertEqual(M.compare(observed,observed)[2],[])
        bad=dict(observed);bad["unapproved"]="a"*64
        with self.assertRaisesRegex(ValueError,"Unapproved"):
            M.compare({},bad)

    def test_review_issue_only_on_real_document_hash_change_never_alert(self):
        source=M.validated_sources()
        repo="ayeemecee0/Katoptron"
        one=hashlib.sha256(b"original").hexdigest()
        two=hashlib.sha256(b"changed official source").hexdigest()
        state={source[0]["id"]:one}
        writes=[];issue=None
        def github(repo_arg,token,method,url,payload=None):
            nonlocal issue
            self.assertEqual(repo_arg,repo)
            writes.append((method,url,payload))
            if method=="GET" and "/issues?" in url:return [] if issue is None else [issue]
            if method=="POST" and url.endswith("/issues"):
                issue={"number":33,"title":payload["title"],"body":payload["body"]}
                return issue
            if method=="PATCH" and url.endswith("/issues/33"):
                issue["body"]=payload["body"];return issue
            raise AssertionError((method,url))
        first=M.publish(repo,"token",state,source,api=github)
        self.assertTrue(first["baseline_created"])
        self.assertEqual(first["alert_events_created"],0)
        self.assertEqual(len([x for x in writes if x[0]=="POST"]),1)
        prior_writes=len(writes)
        second=M.publish(repo,"token",state,source,api=github)
        self.assertFalse(second["baseline_created"])
        self.assertEqual(len(writes),prior_writes+1) # GET only
        change={source[0]["id"]:two}
        revised=M.publish(repo,"token",change,source,api=github)
        self.assertEqual(revised["source_revisions_held_for_review"],1)
        self.assertEqual(revised["alert_events_created"],0)
        self.assertEqual(sum(x[0]=="POST" for x in writes),2)
        self.assertIn("NOT",writes[-2][2]["body"])
        self.assertEqual(M.parse_state(issue["body"])[source[0]["id"]],two)

if __name__=="__main__":unittest.main()
