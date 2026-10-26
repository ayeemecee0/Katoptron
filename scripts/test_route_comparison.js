const assert=require('node:assert/strict');
const Geo=require('../route-geometry.js');
const C=require('../route-comparison.js');
const route={points:[[38.83,-104.81],[38.83,-104.79]],distance:2400,duration:220};
const at=(key,lat,lon,other={})=>({
 record_key:key,latitude:lat,longitude:lon,location_accuracy:'exact',
 last_source_recheck_at:new Date().toISOString(),
 source_flock_label_status:'source_flock_identified',...other});
const first=at('verified-1',38.83,-104.8);
const other=at('verified-2',38.836,-104.8);
const provisional=at('provisional-1',38.83,-104.8,
 {evidence_tier:'independently_corroborated'});
const approx=at('area-1',38.834,-104.8,
 {location_accuracy:'approximate',uncertainty_radius_m:500});
let summary=C.summarize(route,[first,first,other,provisional,approx],Geo);
assert.equal(summary.nearby,1,'same camera must not count twice');
assert.equal(summary.approx,1);
assert.equal(summary.overdue,0);
assert.equal(summary.unknown,0);
assert.equal(C.summarize(route,[provisional],Geo).nearby,0);
const cityGenericLpr=at('live-oak-city-lpr',38.83,-104.8,{
  jurisdiction_label:'Live Oak, TX',
  source_url:'https://services9.arcgis.com/xdpiCgT89eSIEpbi/arcgis/rest/services/LiveOakCameras/FeatureServer/0',
  source_flock_label_status:'generic_lpr'
});
assert.equal(C.eligibleForFlockRoute(cityGenericLpr),false,
  'Original city mapped generic LPR is not manufacturer-confirmed Flock');
const genericDifferentSource=at('future-generic-lpr',38.83,-104.8,{
  source_url:'https://city.gov/other-generic-alpr-inventory',
  source_flock_label_status:'generic_lpr',
  evidence_summary:'Police city ALPR camera map near a Flock program'
});
assert.equal(C.summarize(route,[genericDifferentSource],Geo).nearby,0,
  'A future generic government LPR source cannot silently become a Flock route encounter');
assert.equal(C.summarize(route,[at('unknown-source',38.83,-104.8,{
  source_flock_label_status:'unconfirmed',
  evidence_summary:'Agency participates in Flock but this generic GIS point lacks manufacturer evidence'
})],Geo).nearby,0,'Unconfirmed Flock source label must fail closed');
assert.equal(C.eligibleForFlockRoute({record_key:'legacy-no-field'}),false,
  'Legacy/missing manufacturer source evidence must fail closed');
assert.equal(C.summarize(route,[cityGenericLpr],Geo).nearby,0,
  'Live Oak LPR must not inflate Flock-only route encounters');
const unknownManufacturer=at('generic-device',38.83,-104.8,{
  evidence_summary:'Agency map confirms point, NOT per-device manufacturer identity.'
});
assert.equal(C.summarize(route,[unknownManufacturer],Geo).nearby,0);
assert.equal(C.summarize(route,[at('city-attributed-only',38.83,-104.8,
  {evidence_tier:'source_attributed_unconfirmed'})],Geo).nearby,0);
assert.equal(C.eligibleForFlockRoute(first),true,
  'Existing independently Flock-labelled government GIS remains eligible');

assert.equal(C.summarize(route,[],Geo).nearby,0);
assert.ok(!('riskScore' in summary),'no invented confidence or risk score');
summary=C.summarize(route,[at('stale',38.83,-104.8,{
  last_source_recheck_at:'2024-01-01T00:00:00Z'}),
  at('unknown',38.83,-104.8,{last_source_recheck_at:null})],Geo);
assert.equal(summary.overdue,1);
assert.equal(summary.unknown,1);
assert.equal(C.reviewFreshness({last_confirmed_on:'2026-01-01'}),'unknown');
assert.throws(()=>C.summarize(route,[{record_key:'x',latitude:'bad'}],Geo),/Invalid/);
assert.throws(()=>C.summarize(route,[first],null),/Cannot compare/);
console.log('Evidence-aware driving-route comparison tests passed');
