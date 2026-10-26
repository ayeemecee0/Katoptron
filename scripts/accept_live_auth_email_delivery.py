"""Controlled real signup + password-recovery email delivery test.

Runs only in the intended repository's GitHub Actions using the existing
server-only QA credential. Creates two disposable accounts addressed to
owner-controlled Gmail plus aliases. Does not click links or reset an existing
account password. Never print email, credentials, tokens, or message links.
"""
import hashlib
import json
import os
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://bpvkapswslmgfazbzpsv.supabase.co"
SITE = "https://ayeemecee0.github.io/Katoptron/submit.html"
PUBLIC_KEY = "sb_publishable_JdCkRi7LLLnzBVeEY3WVPQ_3zou_rrW"
OWNER_EMAIL_SHA256 = "8b89e2d99a037b83fb9beacf3ff9140f8d9a1839fffe81043b9762a6f4927e8b"

class SafeFailure(Exception):
    pass

def request(method, path, key, payload=None, ok=(200, 201)):
    assert path.startswith("/") and not path.startswith("//")
    headers = {"apikey": key, "Accept": "application/json",
               "Content-Type": "application/json",
               "User-Agent": "Katoptron-one-shot-email-delivery-qa/1.0"}
    if key.startswith("eyJ"):
        headers["Authorization"] = "Bearer " + key
    req = urllib.request.Request(
        BASE + path, method=method, headers=headers,
        data=None if payload is None else json.dumps(payload).encode("utf-8")
    )
    try:
        with urllib.request.urlopen(req, timeout=22) as resp:
            if resp.status not in ok or resp.geturl() != BASE + path:
                raise SafeFailure("Unexpected API response")
            body = resp.read(250_000)
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as err:
        raise SafeFailure(method + " request returned HTTP " + str(err.code)) from None
    except urllib.error.URLError:
        raise SafeFailure("Production Auth service unavailable") from None

def main():
    if not (os.getenv("GITHUB_ACTIONS") == "true"
            and os.getenv("GITHUB_REPOSITORY") == "ayeemecee0/Katoptron"
            and os.getenv("KATOPTRON_EMAIL_QA") == "true"):
        raise SafeFailure("Email QA restricted to explicit CI")
    private = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not private.startswith(("sb_secret_", "eyJ")):
        raise SafeFailure("Server-only QA credential unavailable")

    # Fail closed: do not accidentally send email to an unrelated Supabase user.
    result = request("GET", "/auth/v1/admin/users?per_page=50&page=1", private)
    users = result.get("users", [])
    if len(users) != 1:
        raise SafeFailure("Expected one existing account; QA aborted without sending")
    owner = users[0].get("email", "").strip().lower()
    if (hashlib.sha256(owner.encode()).hexdigest() != OWNER_EMAIL_SHA256
            or not users[0].get("email_confirmed_at")):
        raise SafeFailure("Gmail owner verification did not match; no email sent")
    local, at, domain = owner.partition("@")
    if not at or domain != "gmail.com":
        raise SafeFailure("Expected owner-controlled Gmail aliases")
    nonce = secrets.token_hex(7)
    signup_email = f"{local}+katoptron-qa-signup-{nonce}@{domain}"
    recovery_email = f"{local}+katoptron-qa-recovery-{nonce}@{domain}"
    redirect = "?redirect_to=" + urllib.parse.quote(SITE, safe="")

    # Public, normal user flow; do not admin-confirm this user.
    print("Signup: requesting genuine email confirmation; delivery unverified")
    signup = request("POST", "/auth/v1/signup" + redirect, PUBLIC_KEY, {
        "email": signup_email,
        "password": secrets.token_urlsafe(25) + "Aa1!",
        "data": {"katoptron_email_qa": True},
    })
    if not signup.get("id") and not signup.get("user", {}).get("id"):
        raise SafeFailure("Signup did not produce a disposable Auth user")
    print("SIGNUP REQUEST ACCEPTED (not yet delivery proof)")

    # A separate already-confirmed *disposable* account exercises recovery
    # without touching the owner's password or invalidating signup proof.
    print("Recovery: creating a separate confirmed disposable test identity")
    recovered = request("POST", "/auth/v1/admin/users", private, {
        "email": recovery_email,
        "password": secrets.token_urlsafe(25) + "Aa1!",
        "email_confirm": True,
        "app_metadata": {"katoptron_email_qa": True},
    })
    if not recovered.get("id"):
        raise SafeFailure("Disposable recovery account creation failed")
    request("POST", "/auth/v1/recover" + redirect, PUBLIC_KEY, {
        "email": recovery_email
    })
    print("RECOVERY REQUEST ACCEPTED (not yet delivery proof)")
    print("All test identities are disposable Gmail aliases. No original user password changed.")
    print("Await separate inbox confirmation before claiming delivery.")

if __name__ == "__main__":
    try:
        main()
    except SafeFailure as ex:
        print("LIVE EMAIL QA BLOCKED:", str(ex), file=sys.stderr)
        raise SystemExit(1)
