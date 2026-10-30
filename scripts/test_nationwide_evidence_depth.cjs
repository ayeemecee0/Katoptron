'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict');
const data=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const triage=data('data/nationwide-original-change-and-legacy-hold-triage-2026-10-29.json');
const depth=data('data/nationwide-targeted-agency-original-depth-2026-10-29.json');
const groups=data('data/nationwide-target-agency-original-groups-2026-10-29.json');
const newLeads=data('data/nationwide-original-research-leads-expanded-2026-10-29.json');
const oldLeads=data('data/nationwide-original-source-research-leads-2026-10-29.json');
assert.equal(triage.changed_candidates_count,15);
assert.equal(triage.held_originals_count,13);
assert.equal(new Set(triage.changed_candidates.map(x=>x.source_id)).size,15);
assert.equal(new Set(triage.held_originals.map(x=>x.source_id)).size,13);
assert(triage.changed_candidates.every(x=>/^[a-f0-9]{64}$/.test(x.old_observed_sha256)&&
 /^[a-f0-9]{64}$/.test(x.new_observed_sha256)&&
 x.new_observed_sha256!==x.old_observed_sha256&&
 x.material_documentary_difference_verified===false&&
 x.triage_status==='held_previous_full_original_not_archived'));
assert(triage.held_originals.every(x=>x.original_evidence_retained===true&&x.replacement_id));
const base=data('data/nationwide-original-government-source-receipts.json').receipts;
const old=new Map(base.map(x=>[x.source_id,x]));
for(const r of triage.changed_candidates)assert.equal(r.old_observed_sha256,old.get(r.source_id).sha256_at_observation);
assert.equal(depth.sources.length,11);
assert.equal(groups.groups.length,8);
assert(groups.groups.every(x=>x.independently_identified_originals.length>=2&&!x.comprehensive_agency_records_inventory&&
 !x.documentary_difference_verified&&x.unresolved_gaps.length));
const allSources=[...depth.sources,...data('data/nationwide-recovery-government-originals-2026-10-29.json').original_source_recovery_candidates];
const alt=new Set(allSources.map(x=>x.id));
assert(triage.held_originals.every(x=>alt.has(x.replacement_id)));
assert.equal(newLeads.leads.length,12);
assert.equal(oldLeads.leads.length,3);
const ids=new Set(),urls=new Set();
for(const lead of [...oldLeads.leads,...newLeads.leads]){
 assert(!ids.has(lead.id));ids.add(lead.id);
 assert(lead.source_url.startsWith('https://')&&!lead.source_url.includes('<'));
 assert.equal(lead.camera_coordinates_republished,false);
 assert.equal(lead.policy_enactment_inferred,false);
 assert(lead.what_is_unknown.length>=2&&lead.verified_boundary.length>=45);
 urls.add(lead.source_url);
}
assert.equal(ids.size,15);assert(urls.size>=14);
const script=fs.readFileSync('scripts/watch_nationwide_government_originals.py','utf8');
for(const word of ['agency_depth_sources()','depth_receipts','LEGACY_GOV_HOSTS','public_dns'])assert(script.includes(word));
const page=fs.readFileSync('nationwide-document-review.html','utf8');
for(const word of ['changed_candidates_count!==15','held_originals_count!==13','groups.groups.length!==8'])assert(page.includes(word));
const leads=fs.readFileSync('nationwide-research-leads.html','utf8');
assert(leads.includes('payload[1].leads.length!==12'));
console.log('NATIONWIDE_EVIDENCE_DEPTH_PASS: 15 historical hash holds, 13 preserved failures with alternatives, 8 multi-source groups, 12 new cited leads; no automatic factual promotion.');
