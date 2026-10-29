#!/usr/bin/env python3
"""Confirmed-account-only Flock government-source email notifications.

Only source-dated public evidence changes after explicit account opt-in.
Never send existing historical records on initial subscription. Requires
private SMTP secrets in GitHub Actions; no mailbox or service token in HTML.
"""
import json
import os
import smtplib
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.message import EmailMessage


def eligible(category, user):
    return {
      "government_decision": user.get("watch_government") is True,
      "contract_document": (user.get("watch_government") is True or
                            user.get("watch_renewals") is True),
      "contract_renewal": user.get("watch_renewals") is True,
      "vendor_portal_snapshot": user.get("watch_vendor") is True,
      "vendor_count_changed": user.get("watch_vendor") is True,
      "retention_changed": user.get("watch_vendor") is True,
      "sharing_list_changed": user.get("watch_sharing") is True,
      "policy_original_reviewed": user.get("watch_policies") is True,
      "policy_draft_reviewed": user.get("watch_policies") is True,
    }.get(category,False)


def iso_datetime(value):
    if not isinstance(value,str):raise ValueError("Watch date absent")
    try:out=datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError:raise ValueError("Invalid signed source date")
    if out.tzinfo is None:raise ValueError("Timezone missing from watch date")
    return out.astimezone(timezone.utc)


def api(url,secret,path,method="GET",payload=None):
    headers={"apikey":secret,"Authorization":"Bearer "+secret,
             "Content-Type":"application/json","Accept":"application/json"}
    if method=="POST" and path.startswith("flock_watch_deliveries"):
        headers["Prefer"]="resolution=ignore-duplicates,return=minimal"
    req=urllib.request.Request(url.rstrip("/")+"/rest/v1/"+path,
       method=method,
       data=json.dumps(payload).encode("utf8") if payload is not None else None,
       headers=headers)
    with urllib.request.urlopen(req,timeout=35) as response:
        return json.load(response) if method=="GET" or path.startswith("rpc/") else None


def query(url,secret,table,criteria):
    params=urllib.parse.urlencode(criteria,doseq=True)
    rows=api(url,secret,table+"?"+params)
    if not isinstance(rows,list):raise RuntimeError("Unexpected private Watch response")
    return rows


def make_email(recipient,locality,events,from_address):
    msg=EmailMessage()
    msg["From"]=from_address
    msg["To"]=recipient
    msg["Subject"]="Katoptron Government Watch: "+locality.replace("|",", ")
    lines=[
      "Katoptron detected new source-published Flock accountability records for your opted-in locality watch.",
      "Only source-dated government and vendor disclosures are included.",
      "These are NOT live ALPR detections, confirmed camera uptime, or complete agency access logs.",
      "",
    ]
    for event in events:
        lines.extend([
          str(event.get("title","New public document"))[:280],
          "Evidence: "+str(event.get("evidence_tier","not specified")),
          "Source date: "+str(event.get("source_date") or "date not established"),
          str(event.get("summary",""))[:500],
          "Original source: "+str(event.get("source_url","")),
          "",
        ])
    lines.extend([
      "Manage or disable email notifications after signing in:",
      "https://ayeemecee0.github.io/Katoptron/government-watch.html",
      "",
      "You explicitly enabled these alerts for a locality, not a travel route.",
    ])
    msg.set_content("\n".join(lines))
    return msg


def smtp_send(msg,settings):
    host,port,user,password,from_address=settings
    if port==465:
        with smtplib.SMTP_SSL(host,port,timeout=35,context=ssl.create_default_context()) as smtp:
            smtp.login(user,password)
            smtp.send_message(msg)
    elif port==587:
        with smtplib.SMTP(host,port,timeout=35) as smtp:
            smtp.ehlo()
            smtp.starttls(context=ssl.create_default_context())
            smtp.ehlo()
            smtp.login(user,password)
            smtp.send_message(msg)
    else:raise ValueError("Only encrypted SMTP ports 465 or 587 supported")


def deliver(url,secret,settings,send=smtp_send):
    subscribers=api(url,secret,"rpc/flock_watch_delivery_candidates","POST",{})
    if not isinstance(subscribers,list):raise RuntimeError("Protected Watch recipients unavailable")
    delivered=0
    for sub in subscribers[:500]:
        locality=sub.get("locality_key")
        if not locality or not sub.get("email"):continue
        since=iso_datetime(sub["subscribed_at"])
        policy_rows=query(url,secret,"flock_watch_subscriptions",{
          "select":"watch_policies,policy_opted_in_at",
          "user_id":"eq."+str(sub["user_id"]),
          "locality_key":"eq."+locality,"limit":"2"
        })
        if len(policy_rows)!=1:
            raise RuntimeError("Policy opt-in subscription state missing or ambiguous")
        policy_row=policy_rows[0]
        policy_since=(iso_datetime(policy_row["policy_opted_in_at"])
            if policy_row.get("watch_policies") is True and policy_row.get("policy_opted_in_at")
            else None)
        events=query(url,secret,"flock_agency_watch_events",{
          "select":"event_key,kind,title,summary,source_url,source_date,evidence_tier,observed_at",
          "locality_key":"eq."+locality,
          "observed_at":"gt."+since.isoformat(),
          "order":"observed_at.asc","limit":"30"
        })
        existing=query(url,secret,"flock_watch_deliveries",{
          "select":"event_key","user_id":"eq."+sub["user_id"],
          "locality_key":"eq."+locality,"limit":"1000"
        })
        receipts={x["event_key"] for x in existing}
        unsent=[]
        for event in events:
            observed=iso_datetime(event["observed_at"])
            if event["event_key"] in receipts or observed<=since:
                continue
            policy=event["kind"] in ("policy_original_reviewed","policy_draft_reviewed")
            if policy:
                if policy_since is None or observed<=policy_since:
                    continue
                allowed=True
            else:
                allowed=eligible(event["kind"],sub)
            if allowed:unsent.append(event)
            if len(unsent)>=8:break
        if not unsent:continue
        message=make_email(sub["email"],locality,unsent,settings[4])
        send(message,settings)
        receipts_to_add=[{"user_id":sub["user_id"],"locality_key":locality,
                          "event_key":x["event_key"]} for x in unsent]
        api(url,secret,"flock_watch_deliveries?on_conflict=user_id,locality_key,event_key",
          "POST",receipts_to_add)
        delivered+=1
    return delivered


def send_diagnostic(url,secret,settings,send=smtp_send):
    """One manually authorized SMTP test to the sole confirmed opt-in recipient.

    Does not create a real source event or a production delivery receipt.
    Fails closed if there is more than one consenting subscriber, or if the
    confirmed recipient's subscription has been disabled in the meantime.
    """
    candidates=api(url,secret,"rpc/flock_watch_delivery_candidates","POST",{})
    if not isinstance(candidates,list) or len(candidates)!=1:
        raise RuntimeError("Diagnostic requires exactly one confirmed opt-in recipient")
    sub=candidates[0]
    user_id=sub.get("user_id")
    locality=sub.get("locality_key")
    address=sub.get("email")
    if (not isinstance(user_id,str) or not user_id or
        not isinstance(locality,str) or not locality or
        not isinstance(address,str) or "@" not in address or
        not isinstance(sub.get("subscribed_at"),str)):
        raise RuntimeError("Protected diagnostic subscriber is incomplete")
    iso_datetime(sub["subscribed_at"])
    records=query(url,secret,"flock_watch_subscriptions",{
      "select":"email_enabled,watch_government,watch_vendor,watch_sharing,watch_renewals,watch_policies",
      "user_id":"eq."+user_id,"locality_key":"eq."+locality,"limit":"2"
    })
    if (len(records)!=1 or records[0].get("email_enabled") is not True or
        not any(records[0].get(k) is True for k in (
           "watch_government","watch_vendor","watch_sharing",
           "watch_renewals","watch_policies"))):
        raise RuntimeError("Recipient must have an active category-specific Watch opt-in")
    message=EmailMessage()
    message["From"]=settings[4]
    message["To"]=address
    message["Subject"]="Katoptron Government Watch: TEST EMAIL (not a surveillance event)"
    message.set_content("\n".join([
      "Katoptron Government Watch email delivery test.",
      "",
      "This is a one-time diagnostic email initiated manually by the project operator.",
      "It is NOT a government decision, surveillance change, ALPR observation,",
      "camera detection or report of actual data sharing.",
      "",
      "Your confirmed account has an explicitly enabled locality Watch subscription.",
      "No public evidence, event, subscription or live-delivery receipt was created",
      "or modified to send this test.",
      "",
      "Manage or disable your Watch subscription:",
      "https://ayeemecee0.github.io/Katoptron/government-watch.html",
      "",
      "If you did not request this test, you may disable Watch emails above."
    ]))
    send(message,settings)
    return 1


def main():
    env=os.environ
    url=env.get("SUPABASE_URL")
    key=env.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:raise RuntimeError("No private Supabase Watch credentials")
    fields=("WATCH_SMTP_HOST","WATCH_SMTP_PORT","WATCH_SMTP_USER",
            "WATCH_SMTP_PASSWORD","WATCH_SMTP_FROM")
    diagnostic=(len(sys.argv)==2 and sys.argv[1]=="--diagnostic")
    if len(sys.argv)>1 and not diagnostic:
        raise ValueError("Unrecognized Watch sender mode")
    if not all(env.get(k) for k in fields):
        if diagnostic:raise RuntimeError("Diagnostic requires configured encrypted SMTP sender")
        print("Watch email sender NOT ACTIVE: encrypted SMTP settings missing.")
        print("Evidence synchronization remains active. Zero email alerts sent.")
        return
    settings=(env[fields[0]],int(env[fields[1]]),env[fields[2]],env[fields[3]],env[fields[4]])
    if settings[1] not in (465,587):raise ValueError("Only encrypted SMTP transport permitted")
    if diagnostic:
        count=send_diagnostic(url,key,settings)
        print("One consented diagnostic email accepted by encrypted SMTP:",
              count,"; mailbox arrival must be confirmed separately. No public source events or delivery receipts created.")
        return
    count=deliver(url,key,settings)
    print("Source-qualified opt-in email digests delivered:",count,
          "(no email addresses or subscriber identities logged)")


if __name__=="__main__":
    try:main()
    except Exception as exc:
        raise SystemExit("Watch sender held: "+type(exc).__name__+
                         " (inspect protected workflow configuration)") from None
