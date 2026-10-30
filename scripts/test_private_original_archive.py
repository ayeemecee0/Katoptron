#!/usr/bin/env python3
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
import private_original_archive as a

class MockGateway:
 def __init__(self):self.files={}
 def upload(self,blob,*,source_id=None,sha256=None,kind=None,state=False):
  k="state" if state else (source_id,sha256,kind)
  self.files[k]=blob
 def download(self,*,source_id=None,sha256=None,kind=None,state=False):
  import urllib.error
  k="state" if state else (source_id,sha256,kind)
  if k not in self.files:raise urllib.error.HTTPError("mock://",404,"Not Found",{},None)
  blob=self.files[k]
  if not state and a.digest(blob)!=sha256:raise ValueError("Archived original failed SHA-256 verification")
  return blob

class Archive(unittest.TestCase):
 def fixture(self,root):
  original=b"<html><body>Real original public government policy</body></html>"
  sha=a.digest(original);sid="test-00001"
  base=root/"baseline";base.mkdir()
  (base/(sid+".html")).write_bytes(original)
  manifest={"schema_version":1,"sources":{sid:{"kind":"html","sha256":sha,"observed_on":"2026-10-30"}},"seen_pairs":{}}
  (base/"manifest.json").write_text(json.dumps(manifest))
  rows=[{"source_id":"test-"+str(i).zfill(5),"kind":"html","last_usable_sha256":None} for i in range(100)]
  rows[0]["source_id"]=sid
  rows[0]["last_usable_sha256"]=sha
  snap={"schema_version":2,"observed_on":"2026-10-30","monitored_urls":len(rows),"receipts":rows}
  path=root/"snapshot.json";path.write_text(json.dumps(snap))
  return base,path,original,sid,sha
 def test_cold_restore_after_complete_cache_deletion(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);base,snap,raw,sid,sha=self.fixture(root)
   gw=MockGateway()
   result=a.backup(gw,base,snap)
   self.assertEqual(result["new_originals"],1)
   self.assertEqual(result["cold_restore_test"],"passed_current_bytes")
   # Simulate zero GitHub Actions cache: no manifest, fingerprint or original files.
   import shutil
   shutil.rmtree(base);snap.unlink()
   restored=a.restore(gw,base,snap,require=True)
   self.assertEqual(restored["state"],"restored")
   self.assertEqual((base/(sid+".html")).read_bytes(),raw)
   self.assertEqual(json.loads(snap.read_text())["monitored_urls"],100)
   self.assertEqual(a.backup(gw,base,snap)["new_originals"],0)
 def test_corrupted_stored_original_is_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);base,snap,raw,sid,sha=self.fixture(root)
   gw=MockGateway();a.backup(gw,base,snap)
   gw.files[(sid,sha,"html")]=b"untrusted data"
   with self.assertRaisesRegex(ValueError,"SHA-256"):a.restore(gw,root/"restore",root/"restored.json",require=True)
 def test_missing_private_index_not_a_fake_restore(self):
  with tempfile.TemporaryDirectory() as tmp:
   gw=MockGateway();root=Path(tmp)
   self.assertEqual(a.restore(gw,root/"baseline",root/"snapshot.json")["state"],"no_prior_private_archive")
   with self.assertRaises(Exception):a.restore(gw,root/"baseline",root/"snapshot.json",require=True)
 def test_manifest_hash_mismatch_fails_closed(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);base,snap,raw,sid,sha=self.fixture(root)
   (base/(sid+".html")).write_bytes(b"tampered")
   with self.assertRaisesRegex(ValueError,"SHA-256"):a.collect(base,snap)
if __name__=="__main__":unittest.main()
