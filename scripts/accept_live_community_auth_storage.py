"""One-shot, disposable REAL Supabase Auth + Storage acceptance.

Does not claim to test email delivery or owner backup restore. Uses three new
admin-confirmed @example.invalid Auth users, a 1x1 synthetic PNG, an explicitly
non-public report, and finally deletes all test content/users. Requires
GitHub Actions and the project's server-only secret. No secrets, coordinates,
URLs, personally identifying strings or report payloads are logged.
"""
import base64
import json
import os
import secrets
import urllib.error
import urllib.parse
import urllib.request
from uuid import UUID
from datetime import datetime,timezone,timedelta

BASE="https://bpvkapswslmgfazbzpsv.supabase.co"
BUCKET="katoptron-community-evidence"
PUBLISHABLE="sb_publishable_JdCkRi7LLLnzBVeEY3WVPQ_3zou_rrW"
PIXEL=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+XjX8AAAAASUVORK5CYII=")

class CheckFailed(Exception): pass

def call(method,path,key,payload=None,mime="application/json",expect=(200,201,204)):
    if not path.startswith("/") or path.startswith("//") or "\n" in path:
        raise CheckFailed("Unsafe API path")
    body=None if payload is None else (
        bytes(payload) if isinstance(payload,(bytes,bytearray)) else
        json.dumps(payload,separators=(",",":")).encode())
    # Opaque sb_secret_/sb_publishable_ keys are API keys, not JWTs.
    # Real user Auth access tokens must instead be sent as Bearer JWTs
    # alongside the project's browser-safe publishable apikey.
    privileged=key==os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    api_key=key if privileged else PUBLISHABLE
    headers={
        "apikey":api_key,
        "Content-Type":mime,"Accept":"application/json",
        "User-Agent":"Katoptron-private-acceptance/1.0"
    }
    if key.startswith("eyJ") and not privileged:
        headers["Authorization"]="Bearer "+key
    elif privileged and key.startswith("eyJ"):
        headers["Authorization"]="Bearer "+key
    req=urllib.request.Request(BASE+path,data=body,method=method,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=22) as response:
            if response.status not in expect or response.geturl()!=BASE+path:
                raise CheckFailed("Unexpected API response")
            b=response.read(750_000)
            if len(b)>749_999:raise CheckFailed("Oversized API response")
            return json.loads(b) if b else None
    except urllib.error.HTTPError as ex:
        category=("auth-admin" if path.startswith("/auth/v1/admin/") else
                  "auth-password" if path.startswith("/auth/v1/token") else
                  "storage" if path.startswith("/storage/") else
                  "review" if "/rpc/" in path else "data")
        raise CheckFailed("API "+category+" "+method+" failed with HTTP "+str(ex.code)) from None
    except urllib.error.URLError:
        raise CheckFailed("API unavailable") from None


def download_private_image(path,key):
    """Download one exact private QA byte fixture as its owner, never log it."""
    expected_prefix="/storage/v1/object/authenticated/"+BUCKET+"/"
    url=BASE+expected_prefix+path
    require(path.count("/") == 2 and path.endswith("/evidence.png"),
            "Unexpected private QA object path")
    request=urllib.request.Request(url,method="GET",headers={
      "apikey":PUBLISHABLE,"Authorization":"Bearer "+key,
      "User-Agent":"Katoptron-private-acceptance/1.0","Accept":"image/png"
    })
    try:
        with urllib.request.urlopen(request,timeout=20) as response:
            if response.status!=200 or response.geturl()!=url:
                raise CheckFailed("Private photo content unavailable")
            data=response.read(4096)
            require(len(data)<=2048 and data==PIXEL,
                    "Private restored photo differs from original fixture")
            return data
    except urllib.error.HTTPError as exc:
        raise CheckFailed("Private photo download rejected HTTP "+str(exc.code)) from None

def require(value,reason):
    if not value:raise CheckFailed(reason)

def query(table,select,filter_path,key):
    url="/rest/v1/"+table+"?select="+urllib.parse.quote(select,safe=",()")+"&"+filter_path
    result=call("GET",url,key)
    require(isinstance(result,list),"Unexpected records response")
    return result


def cleanup_recent_orphaned_qa_photo(secret):
    """Remove only very recent orphaned QA evidence with absent Auth and case.

    This is recovery for an earlier failed test, NOT a general Storage janitor.
    Never touch an object that belongs to an existing account or report.
    """
    root=call("POST","/storage/v1/object/list/"+BUCKET,secret,
              {"prefix":"","limit":100})
    require(isinstance(root,list) and len(root)<100,"QA cleanup bucket root too large")
    cleaned=0
    for folder in root:
        name=folder.get("name","")
        try:UUID(name)
        except (ValueError,TypeError,AttributeError):continue
        cases=call("POST","/storage/v1/object/list/"+BUCKET,secret,
                   {"prefix":name,"limit":100})
        require(isinstance(cases,list) and len(cases)<100,"QA cleanup folder too large")
        for entry in cases:
            caseid=entry.get("name","")
            try:UUID(caseid)
            except (ValueError,TypeError,AttributeError):continue
            photos=call("POST","/storage/v1/object/list/"+BUCKET,secret,
                {"prefix":name+"/"+caseid,"limit":20})
            if not isinstance(photos,list) or len(photos)!=1:
                continue
            photo=photos[0]
            if photo.get("name")!="evidence.png":continue
            created=photo.get("created_at")
            if not isinstance(created,str):continue
            try:stamp=datetime.fromisoformat(created.replace("Z","+00:00"))
            except ValueError:continue
            age=datetime.now(timezone.utc)-stamp
            if not timedelta(seconds=0)<=age<=timedelta(minutes=60):continue
            # service_role has intentionally NO SELECT on private
            # submissions. Never widen it for QA. The foreign key to
            # auth.users is ON DELETE CASCADE; require the owner gone.
            try:
                call("GET","/auth/v1/admin/users/"+name,secret)
                continue
            except CheckFailed as ex:
                if "HTTP 404" not in str(ex):raise
            target=name+"/"+caseid+"/evidence.png"
            call("DELETE","/storage/v1/object/"+BUCKET,secret,
                 {"prefixes":[target]},expect=(200,204))
            remaining=call("POST","/storage/v1/object/list/"+BUCKET,secret,
                {"prefix":name+"/"+caseid,"limit":20})
            require(not remaining,"Old QA photo object deletion not confirmed")
            cleaned+=1
    if cleaned:print("RECOVERY PASS: orphaned recent disposable QA Storage object deleted.")

def run():
    require(os.getenv("GITHUB_ACTIONS")=="true" and
            os.getenv("GITHUB_REPOSITORY")=="ayeemecee0/Katoptron" and
            os.getenv("KATOPTRON_LIVE_QA")=="true",
            "Production-disposable test only permitted in explicit CI environment")
    secret=os.environ.get("SUPABASE_SERVICE_ROLE_KEY","")
    require(secret.startswith(("sb_secret_","eyJ")),"Missing CI server credential")
    prefix=secrets.token_hex(12)
    cleanup_recent_orphaned_qa_photo(secret)
    users=[]
    case=None
    path=None
    failures=[]
    try:
        for kind in ("contributor","reviewer","bystander"):
            email="katoptron-qa-"+kind+"-"+prefix+"@example.invalid"
            password=secrets.token_urlsafe(27)+"Aa1!"
            item=call("POST","/auth/v1/admin/users",secret,{
                "email":email,"password":password,"email_confirm":True,
                "app_metadata":{"provider":"email","providers":["email"],"katoptron_qa":True}
            })
            uid=item.get("id")
            require(isinstance(uid,str) and UUID(uid),"Admin-created QA identity invalid")
            users.append({"id":uid,"kind":kind})
            identity=call("POST","/auth/v1/token?grant_type=password",PUBLISHABLE,{
                "email":email,"password":password
            })
            require(identity.get("user",{}).get("id")==uid and
                    isinstance(identity.get("access_token"),str),
                    "Real confirmed-email Auth password sign-in failed")
            users[-1]["token"]=identity["access_token"]
        owner,reviewer,bystander=users
        source="Rollback-only intent: disposable public beta authentication acceptance; never an actual Flock camera."
        payload={"latitude":38.5816,"longitude":-121.4944,
                 "description":source,"consent_to_review":True,"publication_consent":False}
        created=call("POST","/rest/v1/flock_community_submissions?select=submission_id",
                    owner["token"],payload,expect=(201,))
        # Return data from PostgREST requires Prefer: return=representation.
        # Handle the response-less POST by separately reading via owner RLS.
        listing=query("flock_community_submissions","submission_id,publication_consent",
            "limit=10",owner["token"])
        require(len(listing)==1 and listing[0]["publication_consent"] is False,
                "Real contributor private insertion/receipt failed")
        case=listing[0]["submission_id"]
        require(isinstance(case,str) and UUID(case),"Private report identity invalid")
        other=query("flock_community_submissions","submission_id",
            "submission_id=eq."+case,reviewer["token"])
        require(not other,"Separate user can see non-owned private report")
        # Reviewer is NOT privileged before the explicit synthetic allowlist grant.
        try:
            call("POST","/rest/v1/rpc/list_community_review_queue",
                reviewer["token"],{"p_limit":10})
            raise CheckFailed("Unapproved user reached reviewer queue")
        except CheckFailed as e:
            if str(e)=="Unapproved user reached reviewer queue":raise
        # Scoped, temporary QA reviewer; never an existing account.
        call("POST","/rest/v1/editorial_reviewers",secret,{
            "user_id":reviewer["id"],"role":"publisher",
            "granted_by":"disposable-ci-live-qa"},expect=(201,))
        queue=call("POST","/rest/v1/rpc/list_community_review_queue",
            reviewer["token"],{"p_limit":100})
        require(any(x.get("submission_id")==case for x in queue),
                "Approved reviewer cannot read private case")
        path=owner["id"]+"/"+case+"/evidence.png"
        call("POST","/storage/v1/object/"+BUCKET+"/"+path,
            owner["token"],PIXEL,mime="image/png",expect=(200,201))
        # Storage restore drill uses a disposable PRIVATE photo, not any
        # reporter's content. Verify authenticated bytes, remove, re-upload
        # identical bytes, and verify again before continuing the review.
        # Probe unprivileged third-party access, not a deliberately authorized reviewer.
        try:
            download_private_image(path,bystander["token"])
        except CheckFailed as rejection:
            # Supabase Storage sometimes returns 400 for hidden RLS-protected
            # objects. The owner must subsequently read the identical bytes,
            # ruling out a malformed path or missing QA fixture.
            require(any(code in str(rejection) for code in
                        ("HTTP 400", "HTTP 401", "HTTP 403", "HTTP 404")),
                    "Private Storage bystander access denied with documented gateway response")
        else:
            raise CheckFailed("Private Storage allowed unprivileged third-party access")
        original=download_private_image(path,owner["token"])
        call("DELETE","/storage/v1/object/"+BUCKET,secret,
             {"prefixes":[path]},expect=(200,204))
        call("POST","/storage/v1/object/"+BUCKET+"/"+path,
             owner["token"],original,mime="image/png",expect=(200,201))
        restored=download_private_image(path,owner["token"])
        require(original==restored,"Restored synthetic Storage bytes changed")
        own=call("POST","/storage/v1/object/list/"+BUCKET,owner["token"],
            {"prefix":owner["id"]+"/"+case,"limit":20})
        require(any(x.get("name")=="evidence.png" for x in own),
                "Owner cannot enumerate real private uploaded photograph")
        signed=call("POST","/rest/v1/rpc/community_report_attachment_paths",
                    reviewer["token"],{"p_report":case})
        require(any(x.get("object_path")==path for x in signed),
                "Authorized reviewer cannot enumerate real private photo")
        call("POST","/rest/v1/rpc/set_community_review_status",reviewer["token"],{
            "p_id":case,"p_status":"needs_evidence",
            "p_note":"Disposable evidence-only case reviewed in a production API QA; no public camera publication."
        })
        withdrawn=call("POST","/rest/v1/rpc/withdraw_own_community_report",
                       owner["token"],{"p_id":case})
        require(withdrawn is True,"Real contributor withdrawal failed")
        after=call("POST","/rest/v1/rpc/community_report_attachment_paths",
                   reviewer["token"],{"p_report":case})
        require(after==[],"Reviewer retained new access to withdrawn photo")
        public=query("flock_camera_locations","record_key",
          "latitude=eq.38.5816&longitude=eq.-121.4944",PUBLISHABLE)
        # Other genuine cameras may share the public test coordinate; assert only
        # that our synthetic report ID cannot appear as a source record key.
        require(all(case not in str(x) for x in public),
                "Synthetic private case linked to a public camera")
        print("LIVE AUTH/STORAGE ACCEPTANCE PASS: three actual Auth JWTs; RLS; "
              "private report; reviewer grant/decision; real photo upload/restore; "
              "withdrawal and reviewer cutoff. Email delivery untested.")
    finally:
        # Fail closed. Cleanup uses known exact test-created identifiers only.
        if path:
            try:call("DELETE","/storage/v1/object/"+BUCKET,secret,
                     {"prefixes":[path]},expect=(200,204))
            except Exception:failures.append("private photo cleanup")
        if case:
            try:call("DELETE","/rest/v1/flock_community_review_history?"
                     "submission_id=eq."+case,secret,expect=(200,204))
            except Exception:failures.append("review history cleanup")
        for u in reversed(users):
            if u["kind"]=="reviewer":
                try:call("DELETE","/rest/v1/editorial_reviewers?user_id=eq."+u["id"],
                         secret,expect=(200,204))
                except Exception:failures.append("reviewer grant cleanup")
            try:call("DELETE","/auth/v1/admin/users/"+u["id"],secret,expect=(200,204))
            except Exception:failures.append("Auth user cleanup")
        # The private submissions table intentionally denies server API
        # direct SELECT. Auth user deletion cascades its reports; confirm
        # absence of both test user accounts via Auth admin instead.
        for u in users:
            try:
                call("GET","/auth/v1/admin/users/"+u["id"],secret)
                failures.append("temporary Auth user persists")
            except CheckFailed as ex:
                if "HTTP 404" not in str(ex):
                    failures.append("Auth user cleanup verification")
        if path:
            try:
                files=call("POST","/storage/v1/object/list/"+BUCKET,secret,
                    {"prefix":path,"limit":10})
                if files:failures.append("private photo persists")
            except Exception:failures.append("private photo cleanup verification")
        if failures:
            raise CheckFailed("QA CLEANUP FAILED: "+", ".join(failures))
        print("LIVE QA CLEANUP PASS: test users, grant, report and photo absent")

if __name__=="__main__":
    try:run()
    except CheckFailed as e:
        print("LIVE QA NOT ACCEPTED:",str(e))
        raise SystemExit(1)
