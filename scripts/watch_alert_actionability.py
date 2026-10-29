"""Source-grounded change explanations for new opted-in Government Watch events.

Explanations describe why a category MAY matter, never invent an operational
change, cost, enacted policy, camera location, or Flock database access log.
"""
from urllib.parse import urlsplit,quote
IMPLICATIONS={
 "government_decision":("An original government decision may change the stated authority or planned oversight of a program.",
  "Check the official motion, vote outcome and whether a later signed agreement or implementation record exists."),
 "contract_document":("A documented contract is useful for tracking authorized vendor terms and financial commitments; it does not establish actual expenditure or deployment.",
  "Check signatures, covered dates, amendment sequence, pricing schedules and payment records."),
 "contract_renewal":("A signed original end date can help monitor a forthcoming renewal decision; it is not proof that renewal occurred.",
  "Request the latest executed amendment or documented nonrenewal decision."),
 "vendor_portal_snapshot":("A dated vendor disclosure is a snapshot, not an independent on-device audit.",
  "Compare two dated snapshots from the same authenticated agency identity before claiming a change."),
 "vendor_count_changed":("A change in source-reported inventory does not independently establish new camera installations.",
  "Request the applicable official inventory, installation receipts and device verification."),
 "retention_changed":("A source-reported retention setting is not independent proof that historical data was deleted.",
  "Compare dated original policy versions with published vendor configuration and change records."),
 "sharing_list_changed":("A reported sharing relationship does not prove an individual agency ran a search.",
  "Confirm source agency identity and the applicable written sharing authorization."),
 "policy_original_reviewed":("A newly reviewed original policy adds documentary evidence but may be an older policy.",
  "Read the effective-date and adoption evidence; compare previous versions without assuming new enactment."),
 "policy_draft_reviewed":("A reviewed draft documents a proposal, not an effective policy.",
  "Look for later council action or signed adoption evidence before describing it as current.")
}
def source_https(url):
 try:
  p=urlsplit(url)
  return bool(p.scheme=="https" and p.hostname and p.hostname.find(".")>0 and
    not p.username and not p.password and not p.fragment and not p.port)
 except (ValueError,TypeError):return False
def insights(event,locality):
 kind=event.get("kind")
 if kind not in IMPLICATIONS:raise ValueError("Watch event category lacks sourced explanation")
 url=event.get("source_url")
 if not source_https(url):raise ValueError("Only valid HTTPS original source links qualify")
 why,action=IMPLICATIONS[kind]
 return {"why":why,"next":action,
  "agency_url":"https://ayeemecee0.github.io/Katoptron/agency-xray.html?place="+quote(locality,safe=""),
  "case_url":"https://ayeemecee0.github.io/Katoptron/research-workspace.html?agency="+quote(locality,safe=""),
  "scope":"Historical original evidence and vendor snapshots are not live surveillance events."}
