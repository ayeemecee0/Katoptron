/* Strict original-authority agency HTML receipts; original PDF reviewed
 * dossier counts, Flock equipment/current access and coordinates remain separate.
 */
(function(root,make){const api=make();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.KatoptronAgencyOriginalHTML=api;})(typeof window!=='undefined'?window:null,function(){'use strict';
const KNOWN=Object.freeze({
  "siloam-springs-ar": {
    "state": "AR",
    "url": "https://siloamsprings.gov/1739/FLOCK-Safety-Cameras",
    "sha": "da82e517470c707250b6a9e4076db4ad3839291b41f7376b30abe7416ea25d56",
    "status": "agency_reports_flock_use"
  },
  "idaho-falls-id": {
    "state": "ID",
    "url": "https://www.idahofallsidaho.gov/2113/Automatic-License-Plate-Readers",
    "sha": "bc9e4571fb3a21754f53aee5a7c39917601d482dfaad1be7c95904e82daf516c",
    "status": "agency_reports_flock_use"
  },
  "lexington-ky": {
    "state": "KY",
    "url": "https://www.lexingtonky.gov/government/departments-programs/public-safety/police/license-plate-readers",
    "sha": "90f41cf40b0767aa374cfedc29e755440fbcaf180e167ad1b7b811653b169144",
    "status": "agency_reports_flock_use"
  },
  "rio-rancho-nm": {
    "state": "NM",
    "url": "https://www.rrnm.gov/5071/Automated-License-Plate-Readers",
    "sha": "614c2b4c32bffeb1efb6943070653638bfceac3f9c73a200847d4f88fdcc614e",
    "status": "agency_reports_flock_use"
  },
  "gallatin-tn": {
    "state": "TN",
    "url": "https://gallatintn.gov/m/newsflash/home/detail/173",
    "sha": "969f906ddada64eeb0c0bd93b875ebaca6f78a1eb01ce541efb8b8f361e3aed6",
    "status": "agency_reports_flock_use"
  },
  "lafayette-in": {
    "state": "IN",
    "url": "https://www.lafayette.in.gov/3787/Flock-Safety-Cameras-Frequently-Asked-Qu",
    "sha": "b0a70f5248d653cfa9921b8dae642f325541f24c5aa60490cdf44126fb1709c1",
    "status": "agency_reports_flock_use"
  },
  "robbinsdale-mn": {
    "state": "MN",
    "url": "https://www.robbinsdalemn.gov/389/4240/Automated-License-Plate-Readers-ALPR",
    "sha": "540fe81b203688493e8c5dc467350a2d5fa7aa1f58ded205ff6d17f75a9223a8",
    "status": "agency_reports_flock_use"
  },
  "columbia-mo": {
    "state": "MO",
    "url": "https://beheard.como.gov/safety-cameras-review",
    "sha": "52cdac7bfc6e93ef9988cdd18f8dcd1c1cae0ce3c9bb12c301cc2cb95ef76f8a",
    "status": "agency_reports_flock_use"
  },
  "salem-ma": {
    "state": "MA",
    "url": "https://www.salemma.gov/m/newsflash/home/detail/427",
    "sha": "255d6c8a8462c9dde6596e9e644b8404d0055264bb4efbb0be3a19a5b9ca8a06",
    "status": "announced_not_renewing"
  },
  "south-portland-me": {
    "state": "ME",
    "url": "https://www.southportland.gov/m/newsflash/home/detail/563",
    "sha": "0c19eaab9ec8c36682f0ac24d8c95b0121edc3f8efce7044ac850ea1bd20665d",
    "status": "agency_reports_removed"
  },
  "lafayette-co": {
    "state": "CO",
    "url": "https://www.lafayetteco.gov/m/newsflash/home/detail/10277",
    "sha": "5a3e5f2ef5378e76c0b64bdb12ebfa7b2e29e801e6de2c8fbc9343688e320f46",
    "status": "announced_termination_process"
  }
});
function validate(d){
 if(!d||d.schema_version!==1||d.verified_on!=='2026-10-27'||d.verified_official_publisher_agencies!==11||d.states_with_new_official_publisher_evidence!==11||d.reviewed_pdf_dossiers_added!==0||d.new_verified_exact_camera_points!==0||d.new_verified_live_sharing_edges!==0||!Array.isArray(d.source_disclosures)||d.source_disclosures.length!==11||typeof d.limitations!=='string'||d.limitations.length<160)throw Error('Original publisher disclosure index incomplete');
 const seen=new Set(),states=new Set();
 for(const r of d.source_disclosures){const x=KNOWN[r?.id];if(!x||seen.has(r.id)||states.has(r.state)||r.state!==x.state||r.source_url!==x.url||r.original_html_sha256!==x.sha||r.publisher_statement_category!==x.status||r.evidence_tier!=='agency_official_HTML_claim_anchors_sha256_verified_not_page_reviewed_policy_pdf'||r.source_claim_anchors_verified!==true||!Array.isArray(r.claim_anchors)||r.claim_anchors.length<2||!r.claim_anchors.every(s=>typeof s==='string'&&s.length>=15)||r.policy_enactment_verified!==false||r.current_camera_operation_independently_verified!==false||r.device_coordinates_individually_verified!==0||r.live_sharing_edges_verified!==0)throw Error('Municipal original HTML identity, claim anchors or status changed');seen.add(r.id);states.add(r.state);}
 if(seen.size!==11||states.size!==11)throw Error('Distinct government agency source coverage incomplete');
 return Object.freeze({records:d.source_disclosures.slice().sort((a,b)=>a.state.localeCompare(b.state)),agency_count:11,states_count:11,original_pdf_dossiers_added:0,exact_camera_locations_added:0,verified_live_sharing_edges_added:0});
}
return Object.freeze({validate,KNOWN});
});
