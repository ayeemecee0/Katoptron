/* Katoptron nationwide map + planned-route simulation.
   Source evidence and synthetic observations are deliberately separate. */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const CFG = window.KATOPTRON_CONFIG;
  const Geo = window.KatoptronRouteGeometry;
  const Routing = window.KatoptronRouting;
  const Geoapify = window.KatoptronGeoapify;
  const Provider = window.KatoptronProvider;
  const providerClient = Provider?.client();
  const Comparison = window.KatoptronRouteComparison;
  const RouteEvidence = window.KatoptronRouteEvidence;
  const MAX_VISIBLE = 1200;
  const CAMERA_NEAR_ROUTE_M = 120; // Demonstration proximity threshold, NOT a device read range.
  const USA_CENTER = [39, -98];
  let communityRouteCompare=null;
  const state = {
    map: null, pointLayer: null, areaLayer: null, routeLayer: null, simLayer: null,
    visible: [], tiered: [], tieredUnavailable: false, areas: [], programs: [], agendaMentions: [], route: null, routeRecords: [], routeCoverage: 'unchecked',
    observations: [], replayTimer: null,
    abort: null, requestNumber: 0, lastGeocodeAt: 0, viewportTimer: null,
    routeChoices: [], routeComparisons: [], routeRequest: 0, evidenceAbort: null,
    routeGeocodeCache: {}, routeProviderAbort: null
  };

  function setText(id, value) { $(id).textContent = String(value); }
  function shortDate(value) { return value ? String(value).slice(0, 10) : 'Date not documented'; }
  function sourceFreshness(record) {
    const value=record.last_source_recheck_at || record.last_confirmed_on;
    if(!value) return 'unknown';
    const ms=Date.parse(value);
    if(!Number.isFinite(ms) || ms>Date.now()+15*60*1000)return 'unknown';
    // Dates without a clock time are evidence dates, not evidence of a
    // successful live fetch within the last 72 hours.
    if(/^\d{4}-\d{2}-\d{2}$/.test(String(value)))return 'unknown';
    return Date.now()-ms>72*60*60*1000?'overdue':'recent';
  }
  function validCoord(lat, lon) {
    return Number.isFinite(lat) && Number.isFinite(lon) &&
      lat >= 17 && lat <= 72 && lon >= -180 && lon <= -64;
  }
  function safeUrl(raw) {
    try { const url = new URL(raw); return url.protocol === 'https:' ? url.href : null; }
    catch (_) { return null; }
  }
  function popupFor(record) {
    const div = document.createElement('div');
    div.className = 'camera-popup';
    function add(tag, txt) {
      const element = document.createElement(tag);
      element.textContent = txt;
      div.append(element);
      return element;
    }
    add('strong', record.label);
    add('span',record.evidence_tier==='source_attributed_unconfirmed'
      ? 'SOURCE-ATTRIBUTED · city-associated GIS map observation, NOT an approved or active Flock camera. Excluded from simulations'
      : record.evidence_tier==='independently_corroborated'
      ? 'PROVISIONAL · independently corroborated, NOT government verified. No detections available'
      : record.evidence_tier==='government_verified'
        ? 'Government verified via independently reviewed alternate authority evidence'
        : record.location_accuracy === 'exact'
          ? 'Source-verified location · actual detections not available'
          : 'Approximate deployment area · NOT an individual camera position');
    add('span', record.jurisdiction_label);
    if(Comparison && !Comparison.eligibleForFlockRoute(record) &&
       !record.evidence_tier) {
      add('small',record.source_flock_label_status==='generic_lpr'
        ? 'AGENCY-MAPPED GENERIC LPR. The individual device manufacturer is not confirmed. This map point is excluded from Flock-only route simulation.'
        : 'FLOCK GIS LABEL UNCONFIRMED. This government-mapped location is not yet source-identified as Flock equipment and is excluded from Flock-only route simulation.');
    }
    add('small', record.evidence_summary);
    if (record.evidence_tier) {
      add('small','Case review: '+shortDate(record.published_at));
      add('small',record.evidence_tier==='source_attributed_unconfirmed'
        ? 'Source publisher association was rechecked. Individual camera manufacturer, installation and active status are UNKNOWN.'
        : 'Underlying evidence must satisfy independent review and time-limited corroboration. Current camera operation remains unknown.');
    } else {
      add('small', 'Source last checked: ' + shortDate(record.last_source_recheck_at || record.last_confirmed_on));
      const freshness=sourceFreshness(record);
      add('small',freshness==='recent'
        ? 'Original-source check: within 72 hours; camera operation still unknown'
        : freshness==='overdue'
          ? 'Original-source check: OVERDUE (more than 72 hours). Treat current placement as uncertain.'
          : 'Original-source check: current freshness unavailable; camera operation and current placement unconfirmed.');
      add('small', 'Published evidence: ' + shortDate(record.published_at));
    }
    // Distinguish a government's OWN GIS host from an externally hosted
    // Esri layer that the agency independently endorses. Neither statement
    // establishes camera uptime or an actual ALPR read.
    const originalEvidence=safeUrl(record.source_url);
    const arcgisExternal=originalEvidence && /^services[0-9]*\.arcgis\.com$/i
      .test(new URL(originalEvidence).hostname);
    add('small',record.evidence_tier==='source_attributed_unconfirmed'
      ? 'Evidence tier: CITY-ASSOCIATED MAP PUBLISHER (UNCONFIRMED) · NOT independently government-verified camera hardware'
      : record.evidence_tier==='independently_corroborated'
      ? 'Evidence tier: INDEPENDENTLY CORROBORATED · provisional map layer, excluded from simulator'
      : record.evidence_tier==='government_verified'
        ? 'Evidence tier: government verified through independently reviewed alternative authority path'
        : record.verification_method === 'official_georeferenced_camera_record_v1'
      ? (arcgisExternal
          ? 'Evidence tier: government-endorsed EXTERNAL ArcGIS point; government does not host this source'
          : 'Evidence tier: original government-operated GIS point')
      : 'Evidence tier: corroborated public source');
    const url = safeUrl(record.source_url);
    if (url) {
      const link = add('a', 'Inspect original evidence ↗');
      link.href = url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
    }
    if(!record.evidence_tier && typeof record.record_key==='string') {
      const btn=add('button','Compare nearby community reports');
      btn.type='button';btn.className='history-button';
      btn.addEventListener('click',async ()=>{
        btn.disabled=true;
        const params=new URLSearchParams({
          select:'government_record_key,matching_status,nearest_osm_key,separation_m,osm_observations_within_30m',
          government_record_key:'eq.'+record.record_key,limit:'2'
        });
        try {
          const response=await fetch(CFG.supabaseUrl.replace(/\/$/,'')+
            '/rest/v1/flock_public_cross_source_proximity?'+params.toString(),{
            headers:{apikey:CFG.supabasePublishableKey},
            cache:'no-store',referrerPolicy:'no-referrer'
          });
          if(!response.ok)throw Error('Source comparison HTTP '+response.status);
          const rows=await response.json();
          if(!Array.isArray(rows)||rows.length!==1||
             rows[0].government_record_key!==record.record_key)
            throw Error('Source comparison incomplete');
          const item=rows[0];
          const n=Number(item.osm_observations_within_30m);
          if(!Number.isSafeInteger(n)||n<0)
            throw Error('Source comparison count invalid');
          add('small',n+' community-mapped OSM observation(s) within 30 meters of this government-source point. Proximity does NOT prove one device or two; never add these counts.');
          if(typeof item.nearest_osm_key==='string'&&
             /^(node|way)\/[1-9][0-9]{0,17}$/.test(item.nearest_osm_key)){
            const link=add('a','Inspect nearest original OSM record');
            link.href='https://www.openstreetmap.org/'+item.nearest_osm_key;
            link.target='_blank';link.rel='noopener noreferrer';
          }
          btn.textContent='Community proximity checked';
        }catch(e){
          btn.disabled=false;
          btn.textContent='Retry community overlap check';
          add('small','Community cross-source comparison unavailable. Missing evidence does not mean zero cameras.');
        }
      });
    }
    if(!record.evidence_tier) {
    const historyButton=add('button','View evidence history');
    historyButton.type='button';
    historyButton.className='history-button';
    historyButton.addEventListener('click',async ()=>{
      historyButton.disabled=true;
      historyButton.textContent='Retrieving history…';
      const q=new URLSearchParams({select:'event_type,recorded_at',
        record_key:'eq.'+record.record_key,order:'recorded_at.desc',limit:'15'});
      try {
        const response=await fetch(CFG.supabaseUrl.replace(/\/$/,'')+
          '/rest/v1/flock_camera_evidence_history?'+q.toString(),
          {headers:{apikey:CFG.supabasePublishableKey},cache:'no-store'});
        if(!response.ok)throw new Error('API HTTP '+response.status);
        const rows=await response.json();
        if(!Array.isArray(rows))throw new Error('Invalid evidence history response');
        const list=document.createElement('ol');
        list.className='evidence-history';
        for(const event of rows){
          const li=document.createElement('li');
          const category={
            published:'Evidence originally published',
            source_rechecked:'Original source rechecked',
            withdrawn:'Record withdrawn'
          }[event.event_type] || 'Evidence event';
          li.textContent=category+' · '+shortDate(event.recorded_at);
          list.append(li);
        }
        if(!rows.length){
          const note=document.createElement('small');
          note.textContent='No public audit entries for this verified record.';
          div.append(note);
        } else div.append(list);
        historyButton.textContent='Evidence history loaded';
      }catch(error){
        historyButton.disabled=false;
        historyButton.textContent='Retry evidence history';
        const status=add('small','History temporarily unavailable: '+error.message);
        status.className='muted';
      }
    });
    } else {
      add('small','This newly reviewed evidence tier does not reuse the canonical GIS source-history ledger.');
    }
    return div;
  }
  function setupMap() {
    if (!window.L) {
      setText('coverageStatus', 'Map library unavailable; try reloading with an internet connection.');
      return;
    }
    const map = L.map('map', {preferCanvas:true, worldCopyJump:false, minZoom:3})
      .setView(USA_CENTER, 4);
    state.map = map;
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors', maxZoom: 19
    }).addTo(map);
    // Government-verified positions render ABOVE community density and OSM dots.
    // Different evidence layers never share a visual pane or publication gate.
    map.createPane('officialEvidencePane');
    map.getPane('officialEvidencePane').style.zIndex='460';
    state.areaLayer = L.layerGroup().addTo(map);
    state.pointLayer = L.layerGroup().addTo(map);
    state.routeLayer = L.featureGroup().addTo(map);
    state.simLayer = L.layerGroup().addTo(map);
    communityRouteCompare=window.KatoptronCommunityRoute?.install({
      cfg:CFG,geo:Geo,showStatus:()=>renderRouteComparisons()
    })||null;
    // Default-on community observations are visually primary but never enter
    // state.visible, government comparisons, or official modeled encounters.
    window.KatoptronCommunityOverlay?.install(map,CFG);
    map.on('moveend', () => {
      clearTimeout(state.viewportTimer);
      state.viewportTimer = setTimeout(loadVisibleLocations, 250);
    });
    loadVisibleLocations();
    loadDocumentedPrograms();
    loadNationalSummary();
    loadCommunityNationalSummary();
    loadCommunityQuality();
    loadLatestProviderHealth();
    loadStateEvidenceIndex();
    loadVerifiedAgendaMentions();
  }
  function renderPrograms() {
    const list=$('programList');
    list.replaceChildren();
    const term=$('programSearch').value.trim().toLowerCase();
    const found=state.programs.filter(p=>
      (p.jurisdiction_label+' '+p.official_claim_summary).toLowerCase().includes(term));
    // Limit initial DOM work while preserving the full searchable source list.
    for(const program of found.slice(0,60)) {
      const item=document.createElement('li');
      const title=document.createElement('strong');
      title.textContent=program.jurisdiction_label;
      const status=document.createElement('span');
      status.className=program.program_status==='terminated_at_source_date'
        ? 'program-ended':'program-documented';
      status.textContent=(program.program_status==='terminated_at_source_date'
        ? 'Program terminated per source · ':'Program documented · ')+shortDate(program.source_date);
      const description=document.createElement('p');
      description.textContent=program.official_claim_summary;
      const evidence=document.createElement('a');
      evidence.textContent='Original government source ↗';
      const original=safeUrl(program.official_evidence_url);
      if(original) {
        evidence.href=original; evidence.target='_blank'; evidence.rel='noopener noreferrer';
      }
      item.append(title,status,description);
      if(original)item.append(evidence);
      // Static, original-government map documents are separate evidence:
      // they show the agency's cartography, not verified lat/lon camera pins.
      const mapUrl=safeUrl(program.official_camera_map_url);
      if(mapUrl && original && new URL(mapUrl).host===new URL(original).host) {
        const link=document.createElement('a');
        link.textContent='Official camera map (illustrative positions) ↗';
        link.href=mapUrl; link.target='_blank'; link.rel='noopener noreferrer';
        item.append(document.createTextNode(' · '),link);
      }
      list.append(item);
    }
    setText('programStatus',(found.length>60 ? 'Showing first 60 of ' : '')+
      found.length+' dated original-government program record(s). '+
      'These are not verified camera coordinates. Narrow the search for more results.');
  }
  async function loadStateEvidenceIndex() {
    if(!CFG?.supabaseUrl || !CFG?.supabasePublishableKey){
      setText('stateEvidenceStatus','State evidence index unavailable.');
      return;
    }
    try {
      const q=new URLSearchParams({
        select:'state_code,verified_camera_points,verified_camera_jurisdictions,dated_program_records,terminated_program_records,vendor_disclosed_agencies',
        order:'verified_camera_points.desc,state_code.asc',limit:'65'
      });
      const response=await fetch(CFG.supabaseUrl.replace(/\/$/,'')+
        '/rest/v1/flock_public_state_evidence_index?'+q.toString(),
        {headers:{apikey:CFG.supabasePublishableKey},cache:'no-store'});
      if(!response.ok)throw new Error('State evidence HTTP '+response.status);
      const rows=await response.json();
      if(!Array.isArray(rows) || rows.length>=65)
        throw new Error('State evidence index truncated');
      const list=$('stateEvidenceList');
      list.replaceChildren();
      for(const item of rows){
        const fields=['verified_camera_points','verified_camera_jurisdictions',
          'dated_program_records','terminated_program_records','vendor_disclosed_agencies'];
        if(!/^[A-Z]{2}$/.test(item.state_code) ||
            fields.some(key=>!Number.isInteger(Number(item[key]))||Number(item[key])<0) ||
            Number(item.terminated_program_records)>Number(item.dated_program_records))
          throw new Error('Malformed state evidence data');
        const li=document.createElement('li');
        const title=document.createElement('strong');
        title.textContent=item.state_code;
        const count=document.createElement('p');
        const pins=Number(item.verified_camera_points);
        count.textContent=pins
          ? pins.toLocaleString()+' verified camera GIS points in '+
            Number(item.verified_camera_jurisdictions)+' sourced jurisdiction(s)'
          : 'No independently verified GIS camera points published; actual coverage unknown';
        li.append(title,count);
        const documented=Number(item.dated_program_records);
        if(documented>0){
          const history=document.createElement('p');
          const stopped=Number(item.terminated_program_records);
          history.textContent=documented+' dated government program record(s)'+
            (stopped?' · '+stopped+' reported terminated':'')+
            '. These records do not locate individual cameras.';
          li.append(history);
        }
        const vendorCount=Number(item.vendor_disclosed_agencies);
        if(vendorCount>0){
          const report=document.createElement('p');
          report.textContent=vendorCount+' agency/agency group(s) with dated Flock Safety first-party portal reports. '+
            'Vendor camera totals are not georeferenced camera pins.';
          li.append(report);
        }
        list.append(li);
      }
      const withoutGeometry=rows.filter(item=>Number(item.verified_camera_points)===0).length;
      setText('stateEvidenceStatus',rows.length+
        ' states with published GIS points, government program evidence or Flock vendor disclosures; '+
        withoutGeometry+' state(s) have no verified GIS camera points. '+
        'No listed records for a state means evidence unknown, not no Flock cameras.');
    }catch(error){
      setText('stateEvidenceStatus','State evidence index unavailable: '+
        error.message+'. Missing data does not establish camera absence.');
    }
  }
  async function loadNationalSummary() {
    if(!CFG?.supabaseUrl || !CFG?.supabasePublishableKey){
      setText('nationalStats','National published evidence counts unavailable.');
      return;
    }
    try {
      const response=await fetch(CFG.supabaseUrl.replace(/\/$/,'')+
        '/rest/v1/flock_public_coverage_stats?select=*',
        {headers:{apikey:CFG.supabasePublishableKey},cache:'no-store'});
      if(!response.ok)throw new Error('HTTP '+response.status);
      const rows=await response.json();
      if(!Array.isArray(rows)||rows.length!==1)
        throw new Error('National evidence response incomplete');
      const metrics=rows[0];
      const keys=['verified_camera_points','verified_point_jurisdictions',
        'verified_area_polygons','documented_government_programs'];
      if(keys.some(key=>!Number.isInteger(Number(metrics[key]))||Number(metrics[key])<0))
        throw new Error('National source counts invalid');
      setText('nationalVerifiedCount',Number(metrics.verified_camera_points).toLocaleString());
      setText('nationalStats',
        Number(metrics.verified_camera_points).toLocaleString()+
        ' verified camera points in '+Number(metrics.verified_point_jurisdictions)+
        ' sourced jurisdictions nationwide · '+
        Number(metrics.verified_area_polygons)+' documented deployment polygons · '+
        Number(metrics.documented_government_programs)+
        ' government program records. Coverage is incomplete, not zero elsewhere.');
    }catch(error) {
      setText('nationalStats','National published evidence totals unavailable: '+
        error.message+'. Missing counts do not mean no cameras.');
    }
  }
  async function loadCommunityQuality() {
    if(!CFG?.supabaseUrl||!CFG?.supabasePublishableKey){
      setText('nationalCommunityQuality','OSM quality measurements unavailable.');
      return;
    }
    try{
      const p=new URLSearchParams({select:'source_snapshot_date,osm_observations,distinct_coordinates,colocated_extra_observations,osm_edits_older_365d',limit:'2'});
      const response=await fetch(CFG.supabaseUrl.replace(/\/$/,'')+
        '/rest/v1/flock_public_osm_latest_quality?'+p.toString(),{
        headers:{apikey:CFG.supabasePublishableKey},
        cache:'no-store',referrerPolicy:'no-referrer'
      });
      if(!response.ok)throw Error('Quality API HTTP '+response.status);
      const rows=await response.json();
      if(!Array.isArray(rows)||rows.length!==1)throw Error('Latest quality receipt unavailable');
      const r=rows[0];
      const nums=['osm_observations','distinct_coordinates','colocated_extra_observations','osm_edits_older_365d'];
      if(nums.some(k=>!Number.isSafeInteger(r[k])||r[k]<0)||
         r.osm_observations!==r.distinct_coordinates+r.colocated_extra_observations)
        throw Error('Malformed quality receipt');
      setText('nationalCommunityQuality',
        'OSM quality as of '+r.source_snapshot_date+': '+
        r.distinct_coordinates.toLocaleString()+' mapped coordinate positions · '+
        r.colocated_extra_observations.toLocaleString()+' additional observations at the same coordinates · '+
        r.osm_edits_older_365d.toLocaleString()+' source records last edited over one year before the import. '+
        'Neither co-location nor old edits prove duplicate or inactive cameras.');
    }catch(err){
      setText('nationalCommunityQuality','OSM source quality measurements unavailable: '+
        err.message+'. Treat missing quality information as unknown.');
    }
  }
  async function loadLatestProviderHealth() {
    if(!CFG?.supabaseUrl||!CFG?.supabasePublishableKey){
      setText('providerHealthPublic','Public provider health record unavailable. Route status unknown.');
      return;
    }
    try{
      const q=new URLSearchParams({
        select:'checked_at,result_code,routing_http_status,geocoding_http_status,browser_test_passed,fixture_type',
        limit:'1'
      });
      const r=await fetch(CFG.supabaseUrl.replace(/\/$/,'')+
        '/rest/v1/flock_public_latest_provider_health?'+q.toString(),{
         headers:{apikey:CFG.supabasePublishableKey},cache:'no-store',
         referrerPolicy:'no-referrer'
        });
      if(!r.ok)throw Error('Public sample health HTTP '+r.status);
      const rows=await r.json();
      if(!Array.isArray(rows)||rows.length!==1){
        setText('providerHealthPublic','No completed scheduled Geoapify sample published yet. Availability unknown.');
        return;
      }
      const health=rows[0],stamp=Date.parse(health.checked_at);
      if(!Number.isFinite(stamp)||stamp>Date.now()+600000||
        health.fixture_type!=='public_fixed_route')
        throw Error('Invalid provider-health source timestamp or scope');
      const ageHours=(Date.now()-stamp)/3600000;
      const asOf=new Date(stamp).toLocaleString();
      if(ageHours>36){
        setText('providerHealthPublic','Last public Geoapify test is stale ('+asOf+
          '). Current provider availability unknown; account-wide remaining quota not available.');
      }else if(health.result_code==='passed'){
        setText('providerHealthPublic','Fixed public Geoapify route and geocode tests passed at '+
          asOf+'. This is not an uptime guarantee or account-wide quota balance.');
      }else{
        setText('providerHealthPublic','Fixed public Geoapify test reported '+
          (health.result_code==='provider_error'?'provider error':'inconclusive results')+
          ' at '+asOf+'. Routing availability unknown; failed queries do not imply absent cameras.');
      }
    }catch(error){
      setText('providerHealthPublic','Public provider health unavailable: '+
        error.message+'. Routing availability unknown.');
    }
  }
  async function loadCommunityNationalSummary() {
    if(!CFG?.supabaseUrl||!CFG?.supabasePublishableKey){
      setText('nationalCommunityStatus','Community nationwide count unavailable.');
      return;
    }
    try{
      const query=new URLSearchParams({
        select:'reported_flock_points,last_dataset_snapshot_date',limit:'2'
      });
      const response=await fetch(CFG.supabaseUrl.replace(/\/$/,'')+
        '/rest/v1/flock_public_osm_community_stats?'+query.toString(),{
         headers:{apikey:CFG.supabasePublishableKey},
         cache:'no-store',referrerPolicy:'no-referrer'
        });
      if(!response.ok)throw new Error('Community evidence HTTP '+response.status);
      const rows=await response.json();
      if(!Array.isArray(rows)||rows.length!==1||
        !Number.isSafeInteger(rows[0].reported_flock_points)||
        rows[0].reported_flock_points<0||
        rows[0].reported_flock_points>200000)
        throw new Error('Community coverage total invalid');
      setText('nationalCommunityCount',rows[0].reported_flock_points.toLocaleString());
      setText('nationalCommunityStatus',
        'Community source snapshot '+(rows[0].last_dataset_snapshot_date||'date unavailable')+
        '. OpenStreetMap observations are not independently confirmed active cameras.');
    }catch(error){
      setText('nationalCommunityStatus','Community source count unavailable: '+
        error.message+'. Unknown is not zero.');
    }
  }
  function renderVerifiedAgendaMentions() {
    const list=$('agendaMapList');
    list.replaceChildren();
    const term=$('agendaMapSearch').value.trim().toLowerCase();
    const matches=state.agendaMentions.filter(m=>
      (m.jurisdiction_label+' '+m.matter_title).toLowerCase().includes(term));
    for(const mention of matches.slice(0,60)) {
      const item=document.createElement('li');
      const title=document.createElement('strong');
      title.textContent=mention.jurisdiction_label;
      const when=document.createElement('span');
      when.className='program-documented';
      when.textContent='Original government agenda · '+shortDate(mention.intro_date);
      const description=document.createElement('p');
      description.textContent=mention.matter_title;
      item.append(title,when,description);
      const url=safeUrl(mention.government_evidence_url);
      if(url) {
        const link=document.createElement('a');
        link.href=url;link.target='_blank';link.rel='noopener noreferrer';
        link.textContent='Original government proceedings ↗';
        item.append(link);
      }
      list.append(item);
    }
    setText('agendaMapStatus',(matches.length>60?'Showing first 60 of ':'')+
      matches.length+' verified government agenda mention(s). '+
      'A mention is not proof of deployment, equipment, or approval.');
  }
  async function loadVerifiedAgendaMentions() {
    if(!CFG?.supabaseUrl || !CFG?.supabasePublishableKey) {
      setText('agendaMapStatus','Original government agenda source unavailable.');
      return;
    }
    const all=[],size=25,cap=2000;
    try {
      for(let offset=0;offset<cap;offset+=size){
        const q=new URLSearchParams({
          select:'tenant,matter_id,jurisdiction_label,matter_title,government_evidence_url,intro_date',
          status:'eq.verified',order:'tenant.asc,matter_id.asc',
          limit:String(size),offset:String(offset)
        });
        const response=await fetch(CFG.supabaseUrl.replace(/\/$/,'')+
          '/rest/v1/verified_flock_agenda_mentions?'+q.toString(),
          {headers:{apikey:CFG.supabasePublishableKey},cache:'no-store'});
        if(!response.ok)throw new Error('Agenda API HTTP '+response.status);
        const rows=await response.json();
        if(!Array.isArray(rows)||rows.length>size)
          throw new Error('Original government agenda response incomplete');
        all.push(...rows);
        if(rows.length<size){
          state.agendaMentions=all;
          renderVerifiedAgendaMentions();
          return;
        }
      }
      throw new Error('Verified government agenda results exceed scan capacity');
    }catch(error){
      setText('agendaMapStatus','Government proceedings unavailable: '+error.message+
        '. Missing records do not establish absence of proceedings.');
    }
  }

  async function loadDocumentedPrograms() {
    if(!CFG?.supabaseUrl || !CFG?.supabasePublishableKey) {
      setText('programStatus','Source configuration unavailable.');
      return;
    }
    // All pages are read with a stable unique key. Do not quietly discard
    // jurisdictions when the published government directory grows beyond 100.
    const pageSize=25,capacity=2000;
    const all=[];
    try {
      for(let offset=0;offset<capacity;offset+=pageSize){
        const query=new URLSearchParams({
          select:'program_key,jurisdiction_label,state_code,program_status,official_evidence_url,official_camera_map_url,official_claim_summary,source_date,reported_camera_count',
          record_status:'eq.verified',order:'program_key.asc',
          limit:String(pageSize),offset:String(offset)
        });
        const response=await fetch(CFG.supabaseUrl.replace(/\/$/,'')+
          '/rest/v1/flock_documented_programs?'+query.toString(),
          {headers:{apikey:CFG.supabasePublishableKey},cache:'no-store'});
        if(!response.ok)throw new Error('Program evidence API HTTP '+response.status);
        const records=await response.json();
        if(!Array.isArray(records)||records.length>pageSize)
          throw new Error('Government program source page invalid');
        all.push(...records);
        if(records.length<pageSize) {
          state.programs=all;
          renderPrograms();
          return;
        }
      }
      throw new Error('Government directory exceeds the verified scan limit');
    }catch(error){
      // An incomplete paged response is UNKNOWN, not evidence of absent
      // programs. Do not replace previous complete evidence with a partial set.
      setText('programStatus','Documented-program directory unavailable: '+error.message);
    }
  }
  function publicCameraUrl(bounds) {
    const query = new URLSearchParams({
      select: 'id,record_key,label,jurisdiction_label,latitude,longitude,location_accuracy,uncertainty_radius_m,source_type,source_url,evidence_summary,source_flock_label_status,last_confirmed_on,last_source_recheck_at,published_at,verification_method',
      verification_status: 'eq.verified',
      latitude: 'gte.' + bounds.south.toFixed(6),
      longitude: 'gte.' + bounds.west.toFixed(6),
      order: 'published_at.desc',
      limit: String(MAX_VISIBLE)
    });
    query.append('latitude', 'lte.' + bounds.north.toFixed(6));
    query.append('longitude', 'lte.' + bounds.east.toFixed(6));
    return CFG.supabaseUrl.replace(/\/$/, '') +
      '/rest/v1/flock_camera_locations?' + query.toString();
  }
  async function cameraRows(bounds, signal) {
    const response = await fetch(publicCameraUrl(bounds), {
      // Publishable API keys are not user JWTs.
      headers: { apikey: CFG.supabasePublishableKey,Prefer:'count=exact' },
      signal, cache:'no-store'
    });
    if (!response.ok) throw new Error('Camera API HTTP ' + response.status);
    const rows = await response.json();
    if(!RouteEvidence)throw Error('Camera viewport completeness verifier missing');
    const count=RouteEvidence.exactCount(response.headers.get('content-range'),rows);
    if (count>rows.length || rows.length>=MAX_VISIBLE)
      throw new Error('Camera viewport exceeds complete source response; zoom in to reduce density');
    if(rows.some(x=>!x || !validCoord(Number(x.latitude),Number(x.longitude)) ||
      !['exact','approximate'].includes(x.location_accuracy) ||
      typeof x.record_key!=='string' || !x.record_key))
      throw new Error('Camera API returned malformed evidence; no complete-coverage claim possible');
    return rows;
  }
  function publicTieredUrl(bounds) {
    const query=new URLSearchParams({
      select:'case_key,label,jurisdiction_label,latitude,longitude,evidence_tier,evidence_summary,source_url,published_at',
      latitude:'gte.'+bounds.south.toFixed(6),
      longitude:'gte.'+bounds.west.toFixed(6),
      order:'case_key.asc',limit:String(MAX_VISIBLE)
    });
    query.append('latitude','lte.'+bounds.north.toFixed(6));
    query.append('longitude','lte.'+bounds.east.toFixed(6));
    return CFG.supabaseUrl.replace(/\/$/,'')+
      '/rest/v1/flock_public_tiered_camera_points?'+query.toString();
  }
  async function tieredRows(bounds,signal) {
    const response=await fetch(publicTieredUrl(bounds),{
      headers:{apikey:CFG.supabasePublishableKey,Prefer:'count=exact'},signal,cache:'no-store'
    });
    if(!response.ok)throw new Error('Tiered camera API HTTP '+response.status);
    const rows=await response.json();
    if(!RouteEvidence)throw Error('Tiered viewport completeness verifier missing');
    const count=RouteEvidence.exactCount(response.headers.get('content-range'),rows);
    if(count>rows.length||rows.length>=MAX_VISIBLE)
      throw new Error('Tiered source map viewport incomplete; zoom in to narrow evidence density');
    if(rows.some(row=>!row || !validCoord(Number(row.latitude),Number(row.longitude)) ||
        !['government_verified','independently_corroborated','source_attributed_unconfirmed'].includes(row.evidence_tier)))
      throw new Error('Tiered source contained invalid location or classification');
    return rows.map(row=>({
      ...row,record_key:'tiered-'+row.case_key,
      location_accuracy:'exact',uncertainty_radius_m:0,
      published_at:row.published_at,
      last_confirmed_on:null,last_source_recheck_at:null,
      verification_method:row.evidence_tier==='government_verified'
        ?'alternative_government_authority_v1':row.evidence_tier==='source_attributed_unconfirmed'
         ?'source_attributed_gis_unconfirmed_v1':'independent_corroboration_v1'
    }));
  }
  async function routeSourcePage(url,signal){
    if(!RouteEvidence)throw Error('Full-route completeness verifier unavailable');
    const target=new URL(url);
    target.searchParams.set('limit',String(RouteEvidence.PAGE_LIMIT));
    // PostgREST may cap the response below the requested limit. An exact
    // Content-Range total is required before the region can be certified.
    const response=await fetch(target.href,{
      headers:{apikey:CFG.supabasePublishableKey,Prefer:'count=exact'},
      signal,cache:'no-store',referrerPolicy:'no-referrer'
    });
    if(!response.ok)throw Error('Original camera evidence HTTP '+response.status);
    const rows=await response.json();
    const total=RouteEvidence.exactCount(response.headers.get('content-range'),rows);
    return {rows,total};
  }
  async function routeCameraRows(bounds,signal) {
    const [official,tiered]=await Promise.all([
      routeSourcePage(publicCameraUrl(bounds),signal),
      routeSourcePage(publicTieredUrl(bounds),signal)
    ]);
    if(official.rows.some(row=>!row||!validCoord(Number(row.latitude),Number(row.longitude))||
       !['exact','approximate'].includes(row.location_accuracy) ||
       typeof row.record_key!=='string'||!row.record_key))
      throw Error('Government source returned malformed route camera coordinates');
    if(tiered.rows.some(row=>!row||!validCoord(Number(row.latitude),Number(row.longitude))||
       !['government_verified','independently_corroborated','source_attributed_unconfirmed'].includes(row.evidence_tier)))
      throw Error('Government source returned invalid alternative evidence tier');
    tiered.rows=tiered.rows.map(row=>({
      ...row,record_key:'tiered-'+row.case_key,location_accuracy:'exact',
      uncertainty_radius_m:0,last_source_recheck_at:null
    }));
    return {official,tiered};
  }
  // Each real route alternative must finish every source query region. A
  // truncated 1000-row PostgREST response is UNKNOWN, NEVER zero cameras.
  async function collectRouteEvidence(route,signal) {
    if(!Geo||!Comparison||!RouteEvidence)
      throw Error('Route evidence verification library unavailable');
    const scanned=await RouteEvidence.collect(route,Geo,routeCameraRows,
      Comparison.eligibleForFlockRoute,signal);
    const summary=Comparison.summarize(route,scanned.records,Geo,CAMERA_NEAR_ROUTE_M);
    return {status:'complete',records:scanned.records,summary,
      checkedRegions:scanned.checkedRegions,queryRegions:scanned.queries,
      subdivisionCount:scanned.splitRegions};
  }
  function renderRouteComparisons() {
    const list=$('routeComparisonList');
    list.replaceChildren();
    let completed=0,failed=0;
    state.routeChoices.forEach((route,index)=>{
      const evidence=state.routeComparisons[index]||{status:'checking'};
      const selected=route===state.route;
      if(evidence.status==='complete')completed++;
      if(evidence.status==='unavailable')failed++;
      const item=document.createElement('li');
      const button=document.createElement('button');
      button.type='button';
      button.className='comparison-choice'+(selected?' selected':'');
      button.setAttribute('aria-pressed',String(selected));
      button.addEventListener('click',()=>selectRoute(index));
      const heading=document.createElement('strong');
      heading.textContent='Route '+(index+1)+(selected?' · Selected':'');
      const meta=document.createElement('span');
      meta.textContent=kmString(route.distance)+' · about '+Math.round(route.duration/60)+' min';
      const result=document.createElement('small');
      if(evidence.status==='complete') {
        const x=evidence.summary;
        result.textContent=x.nearby+' documented camera point(s) within the illustrative '+
          CAMERA_NEAR_ROUTE_M+' m street-proximity band · '+
          x.approx+' approximate area(s) · '+x.overdue+' stale / '+
          x.unknown+' unknown source-check timestamp(s)';
      }else if(evidence.status==='unavailable') {
        result.textContent='EVIDENCE UNKNOWN · corridor could not be fully checked. '+
          'No absence-of-surveillance claim.';
      }else result.textContent='Checking the full route corridor… camera evidence unknown';
      button.append(heading,meta,result);
      if(communityRouteCompare?.isEnabled()){
        const community=communityRouteCompare.entryFor(route);
        const communityLine=document.createElement('small');
        communityLine.className='community-comparison-evidence';
        communityLine.textContent=window.KatoptronCommunityRoute.format(community,evidence);
        button.append(communityLine);
      }
      item.append(button);list.append(item);
    });
    const total=state.routeChoices.length;
    setText('comparisonStatus',total
      ? completed+'/'+total+' driving routes completely checked against the PUBLISHED inventory'+
        (failed?'; '+failed+' route(s) unavailable':'')+
        '. Differences in documented points do not predict detection or establish a safer route. Unpublished cameras may exist.'
      : 'Plan a route to compare independently checked alternatives. Camera inventory remains incomplete.');
  }
  function displaySelectedRouteEvidence() {
    if(!state.route)return;
    const index=state.routeChoices.indexOf(state.route);
    const evidence=state.routeComparisons[index]||{status:'checking'};
    stopReplay();
    state.simLayer?.clearLayers();
    state.routeRecords=[];
    state.observations=[];
    $('play').disabled=true;
    $('timelineEvents').replaceChildren();
    if(evidence.status==='complete') {
      state.routeCoverage='complete';
      state.routeRecords=evidence.records;
      computeObservations();
      setText('routeStatus','Checked '+evidence.queryRegions+
        ' verified-response camera evidence request(s) across '+evidence.checkedRegions+
        ' complete region(s)'+(evidence.subdivisionCount?' after '+evidence.subdivisionCount+' density subdivision(s)':'')+
        '. Counts cover PUBLISHED records only. Unpublished cameras may still exist.');
      $('play').disabled=false;
    }else if(evidence.status==='unavailable') {
      state.routeCoverage='unavailable';
      setText('nearbyCount','Unknown');
      setText('observationCount','Unknown');
      setText('timelineBadge','DATA INCOMPLETE');
      setText('timelineIntro','Camera evidence could not be checked across the entire selected route. '+
        'No absence of cameras may be inferred. '+evidence.error);
      setText('routeStatus','Evidence unavailable for this alternative. Other alternatives may still be checked.');
    }else{
      state.routeCoverage='checking';
      setText('nearbyCount','…');
      setText('observationCount','…');
      setText('timelineBadge','EVIDENCE CHECK IN PROGRESS');
      setText('timelineIntro','Checking published camera evidence across this full driving alternative; '+
        'unknown results are never treated as zero.');
      setText('routeStatus','Checking selected route. No actual plate detection data is available.');
    }
  }
  async function compareRouteChoices(request) {
    state.evidenceAbort?.abort();
    const controller=new AbortController();
    state.evidenceAbort=controller;
    let next=0;
    async function worker() {
      while(next<state.routeChoices.length && request===state.routeRequest && !controller.signal.aborted){
        const index=next++;
        const route=state.routeChoices[index];
        let outcome;
        try{
          outcome=await collectRouteEvidence(route,controller.signal);
        }catch(error){
          if(controller.signal.aborted || request!==state.routeRequest)return;
          outcome={status:'unavailable',error:String(error.message||'Original source lookup failed').slice(0,190)};
        }
        if(controller.signal.aborted || request!==state.routeRequest ||
          state.routeChoices[index]!==route)return;
        state.routeComparisons[index]=outcome;
        if(communityRouteCompare?.isEnabled())
          communityRouteCompare.updateOfficial(route,outcome);
        if(state.route===route){
          displaySelectedRouteEvidence();

        }
        renderRouteComparisons();
      }
    }
    try{
      await Promise.all(Array.from({length:Math.min(2,state.routeChoices.length)},()=>worker()));
    }finally{
      if(state.evidenceAbort===controller)state.evidenceAbort=null;
    }
  }
  async function loadOfficialAreas(signal,viewport) {
    // Original government polygons may eventually number in the thousands.
    // Read each page to completion, but render only geographic footprints
    // whose bounding rectangles intersect the visible map. Never interpret
    // a truncated list as proof that there are no other deployment areas.
    const pageSize=20,maxRecords=2000;
    const result=[];
    for(let offset=0;offset<maxRecords;offset+=pageSize) {
      const query=new URLSearchParams({
        select:'area_key,jurisdiction_label,area_label,outline_lonlat,evidence_url,evidence_summary,evidence_verified_at',
        geometry_status:'eq.verified',order:'area_key.asc',
        limit:String(pageSize),offset:String(offset)
      });
      const response=await fetch(CFG.supabaseUrl.replace(/\/$/,'')+
        '/rest/v1/flock_documented_coverage_areas?'+query.toString(),
        {headers:{apikey:CFG.supabasePublishableKey},signal,cache:'no-store'});
      if(!response.ok)throw new Error('Area evidence API HTTP '+response.status);
      const records=await response.json();
      if(!Array.isArray(records)||records.length>pageSize)
        throw new Error('Original government area page incomplete');
      for(const area of records) {
        if(!(area && Array.isArray(area.outline_lonlat) &&
          area.outline_lonlat.length>=4 && area.outline_lonlat.length<=250 &&
          area.outline_lonlat.every(vertex=>
            Array.isArray(vertex)&&vertex.length===2&&
            validCoord(Number(vertex[1]),Number(vertex[0]))) &&
          JSON.stringify(area.outline_lonlat[0])===
            JSON.stringify(area.outline_lonlat[area.outline_lonlat.length-1]))) {
          throw new Error('Source-backed deployment polygon malformed');
        }
        const latitudes=area.outline_lonlat.map(pt=>Number(pt[1]));
        const longitudes=area.outline_lonlat.map(pt=>Number(pt[0]));
        if (Math.max(...latitudes)>=viewport.south &&
            Math.min(...latitudes)<=viewport.north &&
            Math.max(...longitudes)>=viewport.west &&
            Math.min(...longitudes)<=viewport.east) {
          result.push(area);
        }
      }
      if(records.length<pageSize)return result;
    }
    throw new Error('Government coverage polygon source scan reached capacity');
  }
  function officialAreaPopup(area) {
    const root=document.createElement('div');
    root.className='camera-popup';
    const title=document.createElement('strong');
    title.textContent=area.area_label;
    const qualifier=document.createElement('p');
    qualifier.textContent='Official documented deployment area, not a camera location. '+
      'No location inside the polygon is proven to contain an active reader.';
    const summary=document.createElement('p');
    summary.textContent=area.evidence_summary;
    const date=document.createElement('small');
    date.textContent='Original area geometry verified: '+shortDate(area.evidence_verified_at);
    root.append(title,qualifier,summary,date);
    const original=safeUrl(area.evidence_url);
    if(original){
      const link=document.createElement('a');
      link.href=original;
      link.target='_blank';link.rel='noopener noreferrer';
      link.textContent='Original government polygon source ↗';
      root.append(document.createElement('br'),link);
    }
    return root;
  }

  async function loadVisibleLocations() {
    if (!state.map || !CFG?.supabaseUrl || !CFG?.supabasePublishableKey) {
      setText('coverageStatus', 'Public database configuration is unavailable.');
      return;
    }
    if (state.abort) state.abort.abort();
    state.abort = new AbortController();
    const requestId = ++state.requestNumber;
    const bounds = state.map.getBounds().pad(0.3);
    const south = Math.max(17, bounds.getSouth());
    const north = Math.min(72, bounds.getNorth());
    const west = Math.max(-180, bounds.getWest());
    const east = Math.min(-64, bounds.getEast());
    if (north < south || east < west) {
      state.visible = [];
      state.tiered=[];
      state.areas = [];
      drawLocations();
      setText('coverageStatus', 'Move the map to a US location to inspect documented coverage.');
      return;
    }
    setText('coverageSpinner', 'Checking live sources…');
    try {
      // Camera points must remain available even if the optional government
      // polygon dataset is not yet reachable through the Data API.
      // Fail the approximate-area indicator separately, never silently
      // converting an unknown area status into a verified zero.
      const [rows,tieredResult,areasResult]=await Promise.all([
        cameraRows({south,north,west,east},state.abort.signal),
        tieredRows({south,north,west,east},state.abort.signal).then(
          value=>({value}),error=>({error})),
        loadOfficialAreas(state.abort.signal,{south,north,west,east}).then(
          value=>({value}),error=>({error}))
      ]);
      if (requestId !== state.requestNumber) return;
      state.visible = rows;
      state.tiered=tieredResult.value || [];
      state.tieredUnavailable=Boolean(tieredResult.error);
      state.areas = areasResult.value || [];
      updateJurisdictions();
      drawLocations();
      if(areasResult.error) setText('areaCount','Unknown');
      setText('coverageSpinner', 'Live data');
      const shown = state.visible.length + state.tiered.length + state.areas.length;
      const capped = state.visible.length >= MAX_VISIBLE;
      const areaWarning=areasResult.error
        ? ' Official deployment-area evidence is temporarily unavailable; area coverage is unknown.'
        : '';
      const tierWarning=tieredResult.error
        ? ' Independently reviewed additional source tier is unavailable; additional camera evidence unknown.'
        : '';
      setText('coverageStatus', (shown
        ? String(shown) + (capped ? '+ records in current viewport. Zoom in to reduce the result limit.' :
           ' source-backed entries in the current map view; not an exhaustive camera census.')
        : 'No source-verified camera coordinates in this view yet. This is an evidence gap, NOT evidence that there are no cameras.') + areaWarning + tierWarning);
    } catch (error) {
      if (error.name === 'AbortError' || requestId !== state.requestNumber) return;
      state.visible = [];
      state.tiered = [];
      state.tieredUnavailable=true;
      state.areas = [];
      updateJurisdictions();
      drawLocations();
      setText('coverageSpinner', 'Source unavailable');
      setText('coverageStatus', 'Unable to load camera evidence (' +
        error.message + '). Camera coverage is unknown; retry by moving the map.');
    }
  }
  function updateJurisdictions() {
    const select=$('jurisdictionFilter');
    const prior=select.value;
    const jurisdictions=[...new Set([...state.visible,...state.tiered,...state.areas]
      .map(x=>x.jurisdiction_label)
      .filter(x=>typeof x==='string'&&x.length<=150))].sort();
    select.replaceChildren();
    const all=document.createElement('option');
    all.value='';all.textContent='All in current map view';
    select.append(all);
    for(const name of jurisdictions){
      const option=document.createElement('option');
      option.value=name;option.textContent=name;
      select.append(option);
    }
    select.value=jurisdictions.includes(prior)?prior:'';
  }
  function recordMatchesFilters(record) {
    const jurisdiction=$('jurisdictionFilter').value;
    const term=$('cameraTextFilter').value.trim().toLocaleLowerCase();
    const searchable=[record.label,record.area_label,record.jurisdiction_label,
      record.evidence_summary].filter(Boolean).join(' ');
    return (!jurisdiction || record.jurisdiction_label===jurisdiction) &&
      (!term || searchable.toLocaleLowerCase().includes(term));
  }
  function drawLocations() {
    if (!state.map) return;
    state.pointLayer.clearLayers();
    state.areaLayer.clearLayers();
    let exact = 0, areas = 0, provisional = 0, attributed = 0, overdue = 0, unknownFreshness = 0;
    for (const record of [...state.visible,...state.tiered]) {
      if (!recordMatchesFilters(record)) continue;
      const p = [Number(record.latitude), Number(record.longitude)];
      if(record.evidence_tier==='source_attributed_unconfirmed') {
         if($('showAttributed').checked) {
           attributed++;
           L.circleMarker(p,{pane:'officialEvidencePane',radius:6,color:'#e1a0ba',weight:2,
             dashArray:'2 4',fillColor:'#b44876',fillOpacity:.55})
             .bindPopup(popupFor(record)).addTo(state.pointLayer);
         }
         continue;
       }
       if (record.evidence_tier==='independently_corroborated') {
        if($('showProvisional').checked) {
          provisional++;
          L.circleMarker(p,{pane:'officialEvidencePane',radius:7,color:'#afc1fa',weight:2,dashArray:'3 3',
            fillColor:'#6587ce',fillOpacity:.6})
            .bindPopup(popupFor(record)).addTo(state.pointLayer);
        }
        continue;
      }
      if (record.location_accuracy === 'exact' && $('showExact').checked) {
        exact += 1;
        const freshness=sourceFreshness(record);
        if(freshness==='overdue')overdue++;
        if(freshness==='unknown')unknownFreshness++;
        L.circleMarker(p, {pane:'officialEvidencePane',radius:6,color:'#0c292e',weight:2,
          fillColor:freshness==='recent'?'#40d8bc':'#cba16e',
          fillOpacity:freshness==='recent'?1:.8})
          .bindPopup(popupFor(record)).addTo(state.pointLayer);
      } else if (record.location_accuracy === 'approximate' && $('showApprox').checked) {
        const radius = Number(record.uncertainty_radius_m);
        if (!(radius >= 250 && radius <= 80000)) continue;
        areas += 1;
        L.circle(p, {radius,color:'#e3ae62',weight:1.5,dashArray:'5 6',
          fillColor:'#e3ae62',fillOpacity:.09})
          .bindPopup(popupFor(record)).addTo(state.areaLayer);
      }
    }
    if ($('showApprox').checked) {
      for(const area of state.areas){
        if(!recordMatchesFilters(area))continue;
        const geometry=area.outline_lonlat.map(([lon,lat])=>[Number(lat),Number(lon)]);
        const polygon=L.polygon(geometry,{
          color:'#e3ae62',weight:1.5,dashArray:'5 6',
          fillColor:'#e3ae62',fillOpacity:.13
        });
        // Display the ORIGINAL polygon rather than a fabricated
        // estimated radius around a city or government agency.
        polygon.bindPopup(officialAreaPopup(area));
        polygon.addTo(state.areaLayer);
        areas++;
      }
    }
    setText('exactCount', exact);
    setText('attributedCount',attributed);
    setText('areaCount', areas);
    setText('provisionalCount',state.tieredUnavailable?'Unknown':provisional);
    const freshnessWarning=(overdue||unknownFreshness)
      ? ' '+overdue+' point source(s) overdue, '+unknownFreshness+
        ' with unknown check freshness; orange pins require caution.'
      : '';
    setText('filterStatus',exact+areas+' government-verified camera or area entries and '+
      provisional+' separately corroborated provisional point(s) and '+attributed+
       ' source-attributed UNCONFIRMED map observation(s) displayed. '+
      'Location precision is source-specific; zero displayed does not mean no cameras.'+
      freshnessWarning);
    // Never apply map UI filters to the full-route evidence queries.
  }
  function rad(n) { return n * Math.PI / 180; }
  function meters(a,b) {
    const dl = rad(b[0]-a[0]), dlon = rad(b[1]-a[1]);
    const v = Math.sin(dl/2)**2 +
      Math.cos(rad(a[0]))*Math.cos(rad(b[0]))*Math.sin(dlon/2)**2;
    return 6371000 * 2 * Math.asin(Math.min(1,Math.sqrt(v)));
  }
  function kmString(m) {
    if (!Number.isFinite(m)) return '—';
    return (m / 1000).toFixed(m < 10000 ? 1 : 0) + ' km';
  }
  function coordinateInput(text) {
    const match = String(text).trim().match(/^(-?\d{1,2}(?:\.\d+)?)\s*,\s*(-?\d{1,3}(?:\.\d+)?)$/);
    if (!match) return null;
    const p = [Number(match[1]), Number(match[2])];
    return validCoord(...p) ? p : null;
  }
  function sleep(ms) { return new Promise(resolve => setTimeout(resolve,ms)); }
  function providerBase(configured, fallback) {
    // This is a PUBLIC no-secret service URL. Keep credentials server-side.
    const raw=configured || fallback;
    const url=new URL(raw);
    if(url.protocol!=='https:' || url.username || url.password ||
       url.search || url.hash || url.port)
      throw new Error('Route/location provider configuration must be an HTTPS base URL without credentials');
    return url.href.replace(/\/$/,'');
  }
  async function getJson(url,timeoutMs,kind,signal) {
    if(!providerClient)throw new Error('Location provider transport unavailable');
    try {
      const data=await providerClient.json(kind,url,timeoutMs,signal);
      setText('providerStatus',(kind==='routing'?'Routing':'Geocoding')+
        (locationProviderMode()==='geoapify'
          ?' via Geoapify responded. Free-tier credits and account quotas apply; future availability is not guaranteed.'
          :' via shared public demonstration provider responded. No availability guarantee.'));
      return data;
    }catch(error){
      if(error.name!=='AbortError')setText('providerStatus',
        'LOCATION PROVIDER DEGRADED · '+error.message+
        ' Do not assume a failed route is camera-free.');
      throw error;
    }
  }
  function locationProviderMode() {
    const mode=CFG.locationProvider||'demo';
    if(!['demo','geoapify'].includes(mode))
      throw new Error('Unknown location provider; refusing an undocumented fallback');
    return mode;
  }
  async function geocodeCandidates(input,signal) {
    const coord=coordinateInput(input);
    if(coord)return [{point:coord,label:input+' (coordinates)'}];
    const q=input.trim();
    if(q.length<3||q.length>160)throw new Error('Enter a more specific location.');
    // Rate-limit shared Photon requests and do not store the query remotely.
    const wait=Math.max(0,1100-(Date.now()-state.lastGeocodeAt));
    if(wait)await sleep(wait);
    state.lastGeocodeAt=Date.now();
    const useFree=locationProviderMode()==='geoapify';
    if(useFree&&!Geoapify)throw new Error('Geoapify adapter unavailable');
    const url=useFree?Geoapify.geocodeUrl(q,CFG)
      :providerBase(CFG.geocodingServiceBase,'https://photon.komoot.io')+
        '/api/?limit=5&lang=en&q='+encodeURIComponent(q);
    const response=await getJson(url,13000,'geocoding',signal);
    const data=useFree?Geoapify.geocodeAsPhoton(response):response;
    if(!Array.isArray(data?.features))
      throw new Error('Geocoding service returned malformed results.');
    const results=[];
    for(const feature of data.features) {
      const coords=feature?.geometry?.coordinates;
      const props=feature?.properties||{};
      if(!Array.isArray(coords)||coords.length<2||
        !validCoord(Number(coords[1]),Number(coords[0])) ||
        String(props.countrycode||'').toUpperCase()!=='US')continue;
      const label=[props.name,props.city,props.state,props.postcode]
        .filter(x=>typeof x==='string'&&x.trim())
        .filter((x,i,a)=>a.indexOf(x)===i).join(', ').slice(0,180)||q;
      const candidate={point:[Number(coords[1]),Number(coords[0])],label};
      if(!results.some(existing=>existing.label===candidate.label &&
          meters(existing.point,candidate.point)<300))results.push(candidate);
    }
    if(!results.length)throw new Error('No US location found for "'+q+'". Try an address or lat,lon.');
    return results;
  }
  async function geocode(input) {
    return (await geocodeCandidates(input))[0]; // Map search, not route routing.
  }
  function clearRouteCandidate(slot) {
    const select=$(slot+'Match');
    select.replaceChildren();
    select.hidden=true;
    select.disabled=true;
    delete state.routeGeocodeCache[slot];
  }
  async function resolveRoutePlace(slot,query,signal) {
    const raw=coordinateInput(query);
    if(raw){
      clearRouteCandidate(slot);
      return {point:raw,label:query+' (coordinates)'};
    }
    const select=$(slot+'Match');
    let cached=state.routeGeocodeCache[slot];
    if(!cached||cached.query!==query) {
      clearRouteCandidate(slot);
      const candidates=await geocodeCandidates(query,signal);
      cached={query,candidates};
      state.routeGeocodeCache[slot]=cached;
      if(candidates.length>1) {
        const prompt=document.createElement('option');
        prompt.value='';
        prompt.textContent='Select the intended US location';
        select.append(prompt);
        candidates.forEach((candidate,index)=>{
          const option=document.createElement('option');
          option.value=String(index);
          option.textContent=candidate.label;
          select.append(option);
        });
        select.hidden=false;
        select.disabled=false;
      }
    }
    if(cached.candidates.length===1)return cached.candidates[0];
    if(!/^\d+$/.test(select.value))return null;
    const index=Number(select.value);
    return cached.candidates[index]||null;
  }
  async function routing(from,to,signal) {
    if(!Routing)throw new Error('Routing verification library unavailable');
    if(locationProviderMode()==='geoapify') {
      if(!Geoapify)throw new Error('Geoapify adapter unavailable');
      const urls=Geoapify.routeUrls(from,to,CFG);
      // Two real routes using separately declared fastest/balanced and shortest
      // objectives. The optional shortest request can fail without replacing
      // the first route with a fabricated alternative.
      const primary=await getJson(urls[0],22000,'routing',signal);
      let short=null;
      try {short=await getJson(urls[1],22000,'routing',signal);}
      catch(error){if(error.name==='AbortError')throw error;}
      return Routing.readAlternatives(
        Geoapify.routingAsOsrm([primary,short]),from,to,Geo);
    }
    const a=from.point,b=to.point;
    const path=String(a[1])+','+String(a[0])+';'+String(b[1])+','+String(b[0]);
    const url=providerBase(CFG.routingServiceBase,
      'https://router.project-osrm.org')+'/route/v1/driving/'+path+
      '?overview=full&geometries=geojson&steps=false&alternatives=true';
    const data=await getJson(url,22000,'routing',signal);
    return Routing.readAlternatives(data,from,to,Geo);
  }
  function sampleIndex(points, proportion) {
    return points[Math.min(points.length-1,Math.round(proportion*(points.length-1)))];
  }
  function nearRoute(point,points) {
    return Geo.closestOnRoute(point,points);
  }
  function formatMinutes(value) { return 'T+' + Math.round(value) + ' min'; }
  function computeObservations() {
    if (!state.route || state.routeCoverage!=='complete') return;
    const points = state.route.points;
    let found = 0;
    const observations = [];
    for (const row of state.routeRecords) {
      if (row.location_accuracy !== 'exact' ||
          !Comparison.eligibleForFlockRoute(row)) continue;
      const close = nearRoute([Number(row.latitude),Number(row.longitude)],points);
      if (close.distance > CAMERA_NEAR_ROUTE_M) continue;
      found += 1;
      const a=points[close.index],b=points[close.index+1];
      const point=[a[0]+close.fraction*(b[0]-a[0]),
        a[1]+close.fraction*(b[1]-a[1])];
      observations.push({kind:'verified',name:row.label,progress:close.progress,
        point,source:row.source_url,sourceFreshness:sourceFreshness(row)});
    }
    const possibleAreas = state.routeRecords.filter(row =>
      row.location_accuracy === 'approximate' &&
      nearRoute([Number(row.latitude),Number(row.longitude)],points).distance <
        Number(row.uncertainty_radius_m) + 1000).length;
    if ($('hypothetical').checked) {
      [0.20,0.45,0.73].forEach((fraction,i)=>{
        observations.push({kind:'hypothetical',name:'Illustrative observation '+(i+1),
          progress:fraction,point:Geo.pointAtProgress(points,fraction),source:null});
      });
    }
    observations.sort((a,b)=>a.progress-b.progress);
    state.observations = observations;
    setText('nearbyCount',found);
    setText('observationCount',observations.length);
    setText('timelineBadge',observations.length+' MODELED EVENTS');
    const areaNote = possibleAreas ?
      String(possibleAreas)+' approximate mapped area(s) intersect the journey; no camera sighting is inferred there. ' : '';
    const overdue=observations.filter(x=>x.kind==='verified' &&
      x.sourceFreshness==='overdue').length;
    const unknown=observations.filter(x=>x.kind==='verified' &&
      x.sourceFreshness==='unknown').length;
    const sourceNote=(overdue||unknown)
      ? String(overdue)+' nearby point source(s) overdue for GIS recheck and '+
        String(unknown)+' with unknown check freshness. Their present-day placement is not established. '
      : '';
    setText('timelineIntro',areaNote+sourceNote+'Potential events are estimates only. '+String(found)+
      ' documented exact point(s) lie within a hypothetical 120 m proximity band (NOT a camera read-range claim).'+
      ($('hypothetical').checked?' Three wholly fictional sample observations are also shown.':''));
    renderTimeline();
  }
  function renderTimeline(limit=state.observations.length) {
    $('timelineEvents').replaceChildren();
    const subset = state.observations.slice(0,Math.min(limit,150));
    if (!subset.length) {
      const li=document.createElement('li');
      li.textContent='No verified camera encounters are established along this route with the current dataset. That does NOT establish surveillance-free travel.';
      $('timelineEvents').append(li);
      return;
    }
    for (const event of subset) {
      const li=document.createElement('li');
      if (event.kind==='verified') li.className='verified';
      const bold=document.createElement('strong');
      const mins=state.route.duration/60 * event.progress;
      bold.textContent=formatMinutes(mins)+' · '+(event.kind==='verified'?'Potential camera proximity':'Fictional sample');
      const sub=document.createElement('small');
      sub.textContent=event.kind==='verified'
        ?event.name+' · Synthetic observation only; detection NOT verified'+
          (event.sourceFreshness==='recent'
            ?' · source rechecked within 72h'
            :' · camera location may be outdated; GIS source check '+
              (event.sourceFreshness==='overdue'?'overdue':'freshness unknown'))
        :'Not a documented camera location or real detection';
      li.append(bold,sub);$('timelineEvents').append(li);
    }
  }
  function renderRoute() {
    state.routeLayer.clearLayers();
    state.simLayer.clearLayers();
    const trip = state.route;
    if (!trip) return;
    L.polyline(trip.points,{color:'#52bce2',weight:5,opacity:.9})
      .addTo(state.routeLayer);
    L.circleMarker(trip.points[0],{radius:8,color:'#0a2931',
      fillColor:'#5edcbd',fillOpacity:1,weight:2}).bindPopup('Starting location')
      .addTo(state.routeLayer);
    L.circleMarker(trip.points[trip.points.length-1],
      {radius:8,color:'#0a2931',fillColor:'#eab76c',fillOpacity:1,weight:2})
      .bindPopup('Destination').addTo(state.routeLayer);
    state.map.fitBounds(state.routeLayer.getBounds().pad(.14));
  }
  function stopReplay() { if (state.replayTimer) clearInterval(state.replayTimer); state.replayTimer=null; }
  function replay() {
    if (!state.route) return;
    stopReplay();state.simLayer.clearLayers();
    let idx=0;
    const events=state.observations;
    renderTimeline(0);
    if (!events.length) {
      setText('routeStatus','No synthetic observations to replay. Camera coverage may be undocumented.');
      return;
    }
    setText('routeStatus','Replaying synthetic potential encounters. This is not Flock tracking data.');
    function frame() {
      if (idx>=events.length) {
        stopReplay();
        setText('routeStatus','Replay complete. These are modeled observations, not real plate reads.');
        return;
      }
      const event=events[idx++];
      const color=event.kind==='verified'?'#51d9be':'#da86db';
      L.circleMarker(event.point,{radius:10,color:'#ffffff',weight:2,
        fillColor:color,fillOpacity:.9}).bindPopup(
          event.kind==='verified'
            ?'Modeled proximity only. '+(event.sourceFreshness==='recent'
              ?'Original GIS recently checked; actual detection is unknown.'
              :'Original GIS freshness uncertain; camera position may have changed.')
            :'Wholly hypothetical sample sighting').addTo(state.simLayer);
      renderTimeline(idx);
    }
    frame();
    state.replayTimer=setInterval(frame,Math.max(400,2400/Math.max(1,events.length)));
  }
  function selectRoute(index) {
    const trip=state.routeChoices[index];
    if(!trip)return;
    state.route=trip;
    $('routeChoice').value=String(index);
    setText('routeDistance',kmString(trip.distance));
    renderRoute();
    $('reset').disabled=false;
    setText('mapLabel','Driving route '+(index+1)+'/'+state.routeChoices.length+': '+
      trip.from+' → '+trip.to);
    displaySelectedRouteEvidence();
    renderRouteComparisons();
    if(communityRouteCompare?.isEnabled())
      communityRouteCompare.select(trip);
  }
  async function planRoute(ev) {
    if (ev) ev.preventDefault();
    if (!state.map) return;
    const from=$('from').value.trim(), to=$('to').value.trim();
    if (!from || !to) return;
    const request=++state.routeRequest;
    state.routeProviderAbort?.abort();
    communityRouteCompare?.cancel();
    const providerController=new AbortController();
    state.routeProviderAbort=providerController;
    $('planRoute').disabled=true;
    stopReplay();
    // A failed second request must never leave the previous route or its
    // verified-camera proximity claims visible for newly entered endpoints.
    state.evidenceAbort?.abort();
    state.evidenceAbort=null;
    state.routeChoices=[];
    state.routeComparisons=[];
    communityRouteCompare?.cancel();
    state.route=null;
    state.routeRecords=[];
    state.routeCoverage='unchecked';
    state.observations=[];
    state.routeLayer?.clearLayers();
    state.simLayer?.clearLayers();
    $('play').disabled=true;
    $('routeChoice').replaceChildren();
    $('routeChoice').disabled=true;
    setText('routeChoiceStatus','Checking newly requested driving route…');
    setText('routeDistance','—');
    setText('nearbyCount','Unknown');
    setText('observationCount','Unknown');
    setText('timelineBadge','NEW ROUTE PENDING');
    setText('timelineIntro','No current route has been validated. Old route evidence has been cleared.');
    $('timelineEvents').replaceChildren();
    renderRouteComparisons();
    setText('routeStatus','Resolving US destinations; contacting routing service…');
    try {
      const a=await resolveRoutePlace('from',from,providerController.signal);
      if(request!==state.routeRequest)return;
      const b=await resolveRoutePlace('to',to,providerController.signal);
      if(request!==state.routeRequest)return;
      if(!a||!b){
        setText('routeStatus','Choose the intended US start and destination matches above, then calculate again. No location was guessed.');
        return;
      }
      const trips=await routing(a,b,providerController.signal);
      if(request!==state.routeRequest)return;
      state.evidenceAbort?.abort();
      state.routeChoices=trips;
      state.routeComparisons=trips.map(()=>({status:'checking'}));
      if(communityRouteCompare?.isEnabled())
        communityRouteCompare.compareAll(trips,state.routeComparisons);
      const select=$('routeChoice');
      select.replaceChildren();
      trips.forEach((trip,index)=>{
        const option=document.createElement('option');
        option.value=String(index);
        option.textContent='Route '+(index+1)+' · '+kmString(trip.distance)+
          ' · about '+Math.round(trip.duration/60)+' min';
        select.append(option);
      });
      select.disabled=trips.length<2;
      setText('routeChoiceStatus',trips.length>1
        ? trips.length+' real driving alternatives available. Switch routes to compare modeled camera proximity.'
        : 'One driving route provided. Other roads may exist but are not verified alternatives.');
      selectRoute(0);
      await compareRouteChoices(request);
    } catch (error) {
      if(request!==state.routeRequest||error.name==='AbortError')return;
      setText('routeStatus','Route unavailable: '+error.message+
        ' No straight-line route or guessed detections will be displayed.');
    } finally {
      if(state.routeProviderAbort===providerController)state.routeProviderAbort=null;
      if(request===state.routeRequest)$('planRoute').disabled=false;
    }
  }
  function reset() {
    ++state.routeRequest;
    state.routeProviderAbort?.abort();
    state.routeProviderAbort=null;
    state.evidenceAbort?.abort();
    state.evidenceAbort=null;
    state.routeChoices=[];
    state.routeComparisons=[];
    communityRouteCompare?.cancel();
    clearRouteCandidate('from');
    clearRouteCandidate('to');
    renderRouteComparisons();
    $('routeChoice').replaceChildren();
    $('routeChoice').disabled=true;
    $('planRoute').disabled=false;
    setText('routeChoiceStatus','Driving alternatives will appear after planning a route.');
    stopReplay();
    state.simLayer.clearLayers();
    state.routeLayer.clearLayers();
    state.route=null;
    state.routeRecords=[];
    state.routeCoverage='unchecked';
    state.observations=[];
    $('play').disabled=true;$('reset').disabled=true;
    setText('routeDistance','—');setText('nearbyCount','—');
    setText('observationCount','—');setText('timelineBadge','NO ROUTE YET');
    setText('timelineIntro','Route planning uses real street geometry when the external router is available. A modeled observation is an illustration, not a record retrieved from Flock.');
    $('timelineEvents').replaceChildren();
    setText('routeStatus','Route cleared. No personal route details were saved by Katoptron.');
    setText('mapLabel','Nationwide OSM reporting density · Official GIS shown separately · Coverage incomplete');
  }
  function bind() {
    $('programSearch').addEventListener('input',renderPrograms);
    $('agendaMapSearch').addEventListener('input',renderVerifiedAgendaMentions);
    $('mapSearchForm').addEventListener('submit',async event=>{
      event.preventDefault();
      const input=$('mapSearch').value.trim();
      if(!input)return;
      setText('mapSearchStatus','Searching US locations…');
      try {
        const result=await geocode(input);
        state.map.setView(result.point,12);
        setText('mapSearchStatus','Map centered on '+result.label+
          '. Camera coverage remains incomplete.');
      }catch(error){
        setText('mapSearchStatus','Map search unavailable: '+error.message);
      }
    });
    $('jurisdictionFilter').addEventListener('change',drawLocations);
    $('cameraTextFilter').addEventListener('input',drawLocations);
    $('showExact').addEventListener('change',drawLocations);
    $('showApprox').addEventListener('change',drawLocations);
    $('showProvisional').addEventListener('change',drawLocations);
    $('showAttributed').addEventListener('change',drawLocations);
    $('compareCommunityRoute').addEventListener('change',()=>{
      if($('compareCommunityRoute').checked&&state.routeChoices.length){
        communityRouteCompare?.compareAll(state.routeChoices,state.routeComparisons);
        communityRouteCompare?.select(state.route);
      }
      renderRouteComparisons();
    });
    $('hypothetical').addEventListener('change',()=>{
      state.simLayer?.clearLayers();
      if (state.routeCoverage==='complete') computeObservations();
    });
    $('routeForm').addEventListener('submit',planRoute);
    for(const slot of ['from','to']) {
      $(slot).addEventListener('input',()=>clearRouteCandidate(slot));
    }
    $('routeChoice').addEventListener('change',()=>selectRoute(Number($('routeChoice').value)));
    $('sampleRoute').addEventListener('click',()=>{
      $('from').value='Sacramento, California';
      $('to').value='Folsom, California';
      planRoute();
    });
    $('play').addEventListener('click',replay);
    $('reset').addEventListener('click',reset);
    $('viewPilot').addEventListener('click',()=>{
      state.map?.setView([47.858,-121.973],13);
    });
    $('viewColorado').addEventListener('click',()=>{
      state.map?.setView([38.85,-104.75],11);
    });
    $('viewPeoria').addEventListener('click',()=>{
      // Extent from the municipality's published Peoria GIS camera inventory.
      state.map?.fitBounds([[33.54,-112.33],[33.81,-112.18]]);
    });
    $('viewLawrenceville').addEventListener('click',()=>{
      state.map?.fitBounds([[33.908,-84.054],[34.002,-83.94]]);
    });
    $('viewWebster').addEventListener('click',()=>{
      state.map?.fitBounds([[29.503,-95.16],[29.566,-95.088]]);
    });
    $('viewNewportBeach').addEventListener('click',()=>{
      // Only the City GIS original point inventory, not a city-wide
      // assertion of operational plate-reader coverage.
      state.map?.fitBounds([[33.554,-117.97],[33.679,-117.81]]);
    });
    $('national').addEventListener('click',()=>{
      state.map?.setView(USA_CENTER,4);
    });
  }
  if(CFG.locationProvider==='geoapify') {
    $('geoapifyAttribution').hidden=false;
    try {
      Geoapify.publicKey(CFG);
      setText('providerStatus','Geoapify free-tier routing and geocoding enabled. '+
        'Usage is subject to its daily credit allowance; camera evidence may be incomplete.');
    }catch(error) {
      setText('providerStatus','Geoapify not ready: '+error.message+
        '. No automatic switch to an unapproved location provider.');
    }
  }else if(CFG.locationProvider!=='demo'&&CFG.locationProvider!==undefined) {
    setText('providerStatus','Invalid routing provider configuration: location searches disabled.');
  }
  bind();
  setupMap();
})();
