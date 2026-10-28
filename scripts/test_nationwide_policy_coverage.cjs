'use strict';
const assert=require('node:assert/strict');
const C=require('../nationwide-policy-coverage.js');
const J=require('../nationwide-jurisdictions.js');
const WA=require('../wa-alpr-registrations.js');
const V=require('../verified-agency-dossiers.js');
const W=require('../wa-original-agency-dossiers.js');
const AP=require('../policy-adoption-evidence.js');
const registry=require('../data/nationwide-government-jurisdiction-registry.json');
const legacy=require('../data/national-government-audit-source-portals.json');
const receipts=require('../data/nationwide-original-government-source-receipts.json');
const registrations=require('../data/wa-original-agency-alpr-registrations.json');
const adoption=require('../data/verified-policy-adoption-status-2026-10-27.json');
const national=require('../data/verified-national-government-documents.json');
const waFlock=require('../data/verified-wa-flock-policy-originals.json');
const waOther=require('../data/verified-wa-agency-policies.json');
const waReceipts=require('../data/wa-ago-original-policy-source-inspection.json');
const base=V.catalog({
 okc:require('../data/verified-okc-2026-original-flock-contract-review.json'),
 ne:require('../data/verified-nebraska-original-aggregate-reports.json'),
 riSd:require('../data/verified-ri-sd-original-alpr-policies.json'),
 kittitas:require('../data/verified-wa-kittitas-scanned-draft-review.json'),
 waRegistry:registrations,
 waHeld:require('../data/wa-held-original-policy-diagnostics.json'),
 national
},{
 okc:require('../okc-original-contracts.js'),
 ne:require('../nebraska-original-aggregate.js'),
 riSd:require('../ri-sd-original-policies.js'),
 kittitas:require('../wa-kittitas-draft-review.js'),
 national:require('../national-primary-documents.js')
});
const waVerified=W.catalog({
 flock:waFlock,other:waOther,registry:registrations,receipts:waReceipts
},{
 flock:require('../wa-reviewed-flock-sources.js'),
 other:require('../wa-original-policies.js')
});
const dossiers=W.combine(base,waVerified);
const input={registry,legacy,receipts,wa:registrations,dossiers,adoption};
const apis={jurisdictions:J,wa:WA,adoption:AP};
const x=C.build(input,apis);
assert.equal(x.counts.states_enrolled,51);
assert.equal(x.counts.state_original_source_seeded,51);
assert.equal(x.counts.original_source_links,57);
assert.equal(x.counts.new_seed_accessible,31);
assert.equal(x.counts.new_seed_held,12);
assert.equal(x.counts.state_ago_registered_agencies,97);
assert.equal(x.counts.individually_source_reviewed_dossier_agencies,18);
assert.equal(x.counts.individually_source_reviewed_original_documents,25);
assert.equal(x.counts.states_with_complete_agency_policy_census,0);
assert.equal(x.counts.verified_current_camera_locations_added,0);
assert.equal(x.counts.verified_current_data_sharing_edges_added,0);
assert.equal(x.source_reviewed_states.length,7,'Exact agency documents are limited to seven states, not all 51');
assert.equal(x.priorities.length,51);
assert.ok(x.priorities.every(p=>p.next_review_status==='research_queue_not_an_enacted_policy_fact'));
assert.equal(x.counts.adopted_ordinance_government_status_records,1);
assert.equal(x.counts.published_unadopted_draft_status_records,1);
const wa=x.states.find(r=>r.state==='WA');
assert.equal(wa.registered.length,97);
assert.ok(wa.reviewed.length>=11);
assert.equal(wa.complete_policy_inventory,false);
assert.equal(wa.flock_cameras_individually_verified_from_sources,0);
assert.ok(wa.registered.every(a=>a.policy_adopted===false&&a.flock_installed_verified===false));
assert.ok(wa.registered.some(a=>a.policy_urls.length>0));
const az=x.states.find(r=>r.state==='AZ');
assert.equal(az.decisions.length,1);
assert.equal(az.decisions[0].status,'adopted_government_original_notice');
assert.equal(az.decisions[0].effective_date,null);
assert.equal(az.decisions[0].camera_coordinates_claimed,0);
const wi=x.states.find(r=>r.state==='WI');
assert.equal(wi.decisions[0].status,'draft_published_no_adoption_verified');
assert.equal(wi.decisions[0].date,null);
assert.ok(wi.reviewed.some(a=>a.agency==='Green Bay Police Department'));
const held=x.states.flatMap(s=>s.sources).filter(s=>s.evidence==='government_source_held');
assert.equal(held.length,12);
assert.ok(held.every(s=>s.document_hash===null&&s.source_page_reviewed===false));
const sourceOnly=x.states.flatMap(s=>s.sources);
assert.equal(sourceOnly.length,57);
assert.ok(sourceOnly.every(s=>s.flock_installed_verified===false&&s.policy_adopted===false));
const o=C.filter(x,'WA','Aberdeen','registered');
assert.equal(o.length,1);
assert.equal(o[0].registered[0].agency,'Aberdeen Police Department');
assert.equal(o[0].reviewed.length,0);
assert.deepEqual(C.filter(x,'WA','Aberdeen','verified'),[]);
assert.equal(C.filter(x,'AZ','','actions')[0].decisions.length,1);
assert.equal(C.filter(x,'WI','','actions')[0].decisions.length,1);
assert.equal(C.filter(x,'AL','','verified').length,0);
assert.equal(C.filter(x,'DC','','sources').length,1);
assert.equal(C.filter(x,'ALL','', 'verified').length,7);
assert.equal(C.filter(x,'MA','Salem','sources').length,1);
function fail(change,expected){
 const cloned=structuredClone(input);change(cloned);
 assert.throws(()=>C.build(cloned,apis),expected);
}
fail(d=>d.dossiers.agencies=51,/counts|ledger/);
fail(d=>d.registry.jurisdictions.pop(),/authentic|census/);
fail(d=>d.wa.registrations[0].registry_status='flock_verified',/Unverified/);
fail(d=>d.dossiers.dossiers[0].documents[0].sha='0',/verification/);
fail(d=>d.receipts.receipts[0].camera_coordinates_verified=true,/attribution/);
fail(d=>d.adoption.records[1].effective_date='2026-09-01',/status|source/);
console.log('NATIONWIDE POLICY COVERAGE PASS: all 51 state source queues, 57 public links, 31 reachable/12 held, 18 original-page agency dossiers, 97 unverified WA registrations, zero statewide completion or new camera claims');
