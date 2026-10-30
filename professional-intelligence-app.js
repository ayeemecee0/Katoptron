/* Public sourced intelligence + strictly opt-in, owner-scoped in-app interests.
 * No server secret, email automation or automatic records-request submission. */
(async function(win){
'use strict';
const $=id=>win.document.getElementById(id),I=win.KatoptronResearchIntelligence;
const element=(tag,t)=>{const el=win.document.createElement(tag);if(t!==undefined)el.textContent=String(t);return el;};
const safeLink=(url,title)=>{if(!I.validUrl(url))throw Error('Unqualified original URL');
 const a=element('a',title);a.href=url;a.rel='noopener noreferrer';a.target='_blank';return a;};
let docket=null,leads=[],issues=[],selected=null,compiledOn=null,eventsKnown=false;
let sb=null,user=null,preferences=[];
function download(name,html){
 const blob=new Blob([html],{type:'text/html'}),url=URL.createObjectURL(blob),a=element('a');
 a.href=url;a.download=name;win.document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),12000);
}
function packageForSelected(){
 if(!selected)throw Error('Select a sourced lead first');
 return I.packageHtml(I.assemblePackage(selected,docket),issues,I.acquisition(selected,docket.rows));
}
function choose(lead){
 selected=lead;
 $('selectedStatus').textContent=lead.label+' · '+lead.source_date+' · '+lead.status;
 $('selectedSummary').replaceChildren(
  element('h3',lead.title),element('p',lead.summary),element('p','Why it may matter: '+lead.why),
  element('p','Government record is not independent verification of current operations or legal compliance.'));
 $('unknowns').replaceChildren();for(const q of lead.unknown)$('unknowns').append(element('li',q));
 $('verifySteps').replaceChildren();for(const s of lead.steps)$('verifySteps').append(element('li',s));
 $('selectedOriginal').href=lead.original_url;
 const ac=I.acquisition(lead,docket.rows);
 $('existingSources').replaceChildren(element('p','Previously indexed source records for '+lead.locality_key+': '+ac.existing.length));
 const ul=element('ul');for(const rec of ac.existing){
  const li=element('li');li.append(safeLink(rec.source_url,rec.title+' ('+rec.source_date+')'));ul.append(li);
 }$('existingSources').append(ul);
 $('draftBody').value=ac.body;
 $('acquisitionStatus').textContent='Custodian to confirm: '+ac.custodian_role+'. Draft prepared, NOT submitted.';
 const route=new URL('./research-workspace.html',win.location.href);
 route.searchParams.set('agency',lead.locality_key);
 route.searchParams.set('title',lead.title.slice(0,150));
 route.searchParams.set('source',lead.original_url);
 $('privateCaseLink').href=route.href;
 $('downloadPackage').disabled=false;$('printPackage').disabled=false;
 $('packageStatus').textContent='Package ready: '+lead.originals.length+' government original(s), citation appendix, unresolved questions and unsent draft. Private cases stay separate.';
 renderComparisons();
}
function renderLeads(){
 $('leadCards').replaceChildren();
 const jurisdiction=$('jurisdiction').value,topic=$('leadTopic').value;
 const ranked=I.rankForResearch(leads,topic,$('leadQuestion').value,jurisdiction);
 const filtered=ranked.map(x=>x.lead);
 for(const entry of ranked.slice(0,55)){
  const lead=entry.lead;
  const b=element('button');b.type='button';b.className=selected?.id===lead.id?'selected':'';
  b.append(element('strong',lead.title),element('small',' · '+lead.locality_key+' · '+lead.label+' · '+lead.source_date),
   element('small',' · Research relevance: '+entry.why_ranked));
  b.addEventListener('click',()=>{choose(lead);renderLeads()});$('leadCards').append(b);
 }
 $('leadStatus').textContent=filtered.length+' source-attributed leads found, displaying '+Math.min(55,filtered.length)+
  '. Historical disclosures are not presented as new alerts.';
 if(!filtered.length)$('leadCards').append(element('p','No matching qualified source records. That does not establish absence of surveillance.'));
}
function renderGapBacklog(){
 $('gapBacklog').replaceChildren();
 const jobs=I.acquisitionBacklog(leads,docket.rows,20);
 for(const task of jobs){
  const article=element('article');article.className='card';
  article.append(element('strong',task.agency+' · '+task.source_date),
   element('p',task.question),element('small','Missing evidence: unverified, NOT proof of misconduct.'));
  const original=safeLink(task.source_url,'Inspect original government document');
  const lead=leads.find(l=>task.task_id.startsWith(l.id+':'));
  const button=element('button','Prepare this targeted request');button.type='button';
  button.addEventListener('click',()=>{
   if(!lead)return;
   choose(lead);
   // Preserve a task-specific request rather than broadening to unrelated questions.
   const single={...lead,unknown:[task.question]};
   $('draftBody').value=I.acquisition(single,docket.rows).body;
   $('acquisitionStatus').textContent='Unsent source-specific request prepared from one documented gap. Verify custodian and date range.';
   $('acquisitionHeading').scrollIntoView({behavior:'smooth',block:'start'});
  });
  article.append(original,element('span',' · '),button);$('gapBacklog').append(article);
 }
 $('gapBacklogStatus').textContent=jobs.length+' source-cited unresolved evidence tasks prepared for review (not 20 newly discovered or fulfilled documents).';
}
function renderComparisons(){
 $('comparisonList').replaceChildren();
 const relevant=issues.filter(x=>!selected||x.locality_key===selected.locality_key).slice(0,20);
 for(const c of relevant){
  const article=element('article');article.className='card';
  article.append(element('strong',c.type.replaceAll('_',' ')),element('p',c.title),
   element('p',c.interpretation),element('small',c.caveat));
  const list=element('ul');
  for(const ref of c.original_refs){
   if(!I.validUrl(ref.url))continue;
   const li=element('li');li.append(safeLink(ref.url,ref.title+(ref.page?' · page '+ref.page:' · exact page not independently verified')));list.append(li);
  }article.append(list);$('comparisonList').append(article);
 }
 $('comparisonStatus').textContent=relevant.length+' source-qualified comparisons/gaps for selected scope. Missing or non-equivalent government disclosures are not labeled misconduct.';
 renderCrossAgency();
}
function renderCrossAgency(){
 const rows=I.crossAgency(docket,$('compareTopic').value);$('crossAgency').replaceChildren();
 const ul=element('ul');for(const r of rows){
  const li=element('li');li.append(safeLink(r.url,r.agency+' · '+r.locality_key+' · '+r.status));
  ul.append(li);
 }$('crossAgency').append(ul,element('p','Different jurisdictions do not establish a legal or factual contradiction. This is a research comparison only.'));
}
async function optionalVerifiedDiffs(){
 try{
  const loader=win.KatoptronOriginalLoader;
  if(!loader||!win.KatoptronChangeTracker||!win.KatoptronVerifiedDiffs||!win.KatoptronInvestigations)return;
  const {index}=await loader.load(win.fetch.bind(win),loader.browserModules(win));
  const urls=['./data/verified-policy-adoption-status-2026-10-27.json',
   './data/apache-junction-adopted-resolution-chapter-2026-10-28.json'];
  const [adoption,apacheResolution]=await Promise.all(urls.map(async url=>{
   const r=await win.fetch(url,{cache:'no-store',referrerPolicy:'no-referrer'});
   if(!r.ok)throw Error('Original change source HTTP '+r.status);return r.json();
  }));
  const events=win.KatoptronChangeTracker.events(win.KatoptronInvestigations.build(index),{adoption,apacheResolution});
  const approved=win.KatoptronVerifiedDiffs.fromEvents(events);
  issues=I.compare(docket,approved);
 }catch(err){$('comparisonStatus').textContent='Page-pinned change comparisons withheld: '+err.message+'. Original source gaps remain available.';}
 renderComparisons();
}
function renderFeed(){
 for(const id of ['newFeed','reviewedFeed','historicalFeed'])$(id).replaceChildren();
 const week=I.digest(leads,preferences);
 $('weeklyDigestStatus').textContent=(user?.email_confirmed_at?'Private source review ready. ':'Sign in to save private follows. ')+
  week.newReviewed.length+' qualifying reviewed government event(s) in the last seven days after follow baseline. No research email automatically sent.';
 const f=I.personalize(leads,preferences);
 const sections=[['newFeed',f.newItems,'No newly published reviewed events since your follow began.'],
  ['reviewedFeed',f.reviewed,'No matching earlier reviewed Watch events.'],
  ['historicalFeed',f.historical,'No matching historical original-government research leads.']];
 for(const [id,items,empty] of sections){
  if(!items.length)$(id).append(element('p',empty));
  for(const l of items.slice(0,12)){
   const btn=element('button',l.title+' · '+l.locality_key+' · '+l.source_date);btn.type='button';
   btn.addEventListener('click',()=>{choose(l);$('leadDetail').scrollIntoView({behavior:'smooth',block:'start'})});
   $(id).append(btn,element('small',' '+l.label+' · '+l.status));
  }
 }
 $('feedStatus').textContent=preferences.length+' private jurisdiction follow(s). '+(eventsKnown?'Reviewed Watch event query succeeded.':'Reviewed Watch feed unavailable; new-event claims are withheld.')+
  ' No email preferences changed.';
}
async function loadFollows(){
 if(!sb||!user)return;
 const {data,error}=await sb.from('research_intelligence_follows').select('locality_key,topics,research_question,opted_in_at')
   .eq('user_id',user.id).order('opted_in_at',{ascending:false}).limit(60);
 if(error)throw Error('Private follow list unavailable: '+error.message);
 preferences=data||[];
 $('followList').replaceChildren();
 for(const p of preferences){
  $('followList').append(element('p',p.locality_key+' · '+p.topics.join(', ')+
   (p.research_question?' · question: '+p.research_question:'')+
   ' · new-event baseline '+p.opted_in_at));
 }
 renderFeed();
}
async function auth(){
 if(!win.supabase||!win.KATOPTRON_CONFIG?.supabasePublishableKey){
  $('feedAuthStatus').textContent='Account service unavailable; public research remains accessible.';return;
 }
 sb=win.supabase.createClient(win.KATOPTRON_CONFIG.supabaseUrl,win.KATOPTRON_CONFIG.supabasePublishableKey);
 const {data,error}=await sb.auth.getUser();
 if(error&&error.name!=='AuthSessionMissingError')throw Error(error.message);
 user=data?.user||null;
 if(!user?.email_confirmed_at){$('signin').hidden=false;$('feedControls').hidden=true;
  $('feedAuthStatus').textContent='Sign in with a confirmed account for private follows. Public research does not require login.';return;}
 $('signin').hidden=true;$('feedControls').hidden=false;
 $('feedAuthStatus').textContent='Confirmed account. In-app follows are private and do not subscribe you to email.';
 await loadFollows();
}
$('signin').addEventListener('submit',async e=>{
 e.preventDefault();
 try{
  const {error}=await sb.auth.signInWithPassword({email:$('email').value.trim(),password:$('password').value});
  $('password').value='';if(error)throw Error(error.message);await auth();
 }catch(err){$('feedAuthStatus').textContent='Sign-in unavailable: '+err.message;}
});
$('logout').addEventListener('click',async()=>{
 if(!sb)return;await sb.auth.signOut();user=null;preferences=[];await auth();
});
$('saveFollow').addEventListener('click',async()=>{
 try{
  if(!user?.email_confirmed_at)throw Error('Confirmed account required');
  const locality_key=$('followJurisdiction').value;
  if(!leads.some(l=>l.locality_key===locality_key))throw Error('Choose an indexed source-backed jurisdiction');
  const tags=[...win.document.querySelectorAll('.followTopic:checked')].map(x=>x.value);
  if(!tags.length||tags.some(x=>!I.TOPICS.includes(x)))throw Error('Choose at least one valid subject');
  const research_question=$('researchQuestion').value.trim();
  if(research_question.length>160)throw Error('Research question too long');
  const existing=preferences.find(p=>p.locality_key===locality_key);
  const query=existing?sb.from('research_intelligence_follows').update({topics:tags,research_question})
    .eq('user_id',user.id).eq('locality_key',locality_key):
    sb.from('research_intelligence_follows').insert({user_id:user.id,locality_key,topics:tags,research_question});
  const {error}=await query;if(error)throw Error(error.message);
  await loadFollows();
  $('feedStatus').textContent='Follow saved. Newly published items are counted only after the database-recorded initial follow time. Historical items stay historical.';
 }catch(err){$('feedStatus').textContent='Follow not saved: '+err.message;}
});
$('copyWeeklyDigest').addEventListener('click',async()=>{
 try{
  if(!user?.email_confirmed_at)throw Error('Sign in with a confirmed account first');
  const week=I.digest(leads,preferences),records=week.newReviewed;
  const out=['Katoptron — seven-day private reviewed-source research summary',
   'Source-qualified, original-government Watch events only; no historical sources presented as new.',
   'New qualifying events: '+records.length,'',
   ...records.flatMap((e,i)=>[(i+1)+'. '+e.title+' · '+e.locality_key,'Source date: '+e.source_date,
     'Status: '+e.status,'Original: '+e.original_url,'Unverified: '+e.unknown.join(' / '),'']),
   'Historical research starters and other unmatched disclosures are excluded from the new-event count.',
   'This is a manually copied research summary, not an automatic email or finding of misconduct.'].join('\n');
  await win.navigator.clipboard.writeText(out);
  $('weeklyDigestStatus').textContent='Seven-day research summary copied from your private follows; no email sent.';
 }catch(e){$('weeklyDigestStatus').textContent='Digest copy unavailable: '+e.message;}
});
$('deleteFollow').addEventListener('click',async()=>{
 try{
  if(!user)throw Error('Sign in first');
  const {error}=await sb.from('research_intelligence_follows').delete()
   .eq('user_id',user.id).eq('locality_key',$('followJurisdiction').value);
  if(error)throw Error(error.message);await loadFollows();
  $('feedStatus').textContent='Private jurisdiction follow erased; no other subscriptions changed.';
 }catch(err){$('feedStatus').textContent='Unfollow failed: '+err.message;}
});
$('copyRequest').addEventListener('click',async()=>{
 try{
  if(!selected)throw Error('Select a source lead');
  await win.navigator.clipboard.writeText($('draftBody').value);
  $('acquisitionStatus').textContent='Editable request copied. No agency submission has occurred.';
 }catch(e){$('acquisitionStatus').textContent='Copy unavailable: '+e.message+'; the draft remains selectable.';}
});
$('downloadPackage').addEventListener('click',()=>{
 try{
  const lead=selected,request=I.acquisition(lead,docket.rows);request.body=$('draftBody').value;
  download('katoptron-investigation-'+lead.id.replace(/[^a-z0-9_-]/gi,'-').slice(0,70)+'.html',
   I.packageHtml(I.assemblePackage(lead,docket),issues,request));
  $('packageStatus').textContent='Printable original-source package saved. No private case materials included.';
 }catch(e){$('packageStatus').textContent='Package withheld: '+e.message;}
});
$('printPackage').addEventListener('click',()=>{
 try{
  const request=I.acquisition(selected,docket.rows);request.body=$('draftBody').value;
  const html=I.packageHtml(I.assemblePackage(selected,docket),issues,request),popup=win.open('','_blank');
  if(!popup)throw Error('Browser blocked print window; download HTML instead');
  popup.document.open();popup.document.write(html);popup.document.close();popup.focus();popup.print();
 }catch(e){$('packageStatus').textContent='Print unavailable: '+e.message;}
});
$('jurisdiction').addEventListener('change',renderLeads);
$('leadTopic').addEventListener('change',renderLeads);
$('leadQuestion').addEventListener('input',renderLeads);
$('compareTopic').addEventListener('change',renderCrossAgency);
try{
 const r=await win.fetch('./data/qualified-original-government-docket-2026-10-29.json',{cache:'no-store',referrerPolicy:'no-referrer'});
 if(!r.ok)throw Error('Original-government docket HTTP '+r.status);
 const input=await r.json();compiledOn=input.compiled_on;
 docket=win.KatoptronGovernmentDocket.build(input);
 const historical=I.leadFromDocket(docket);
 leads=historical;
 // Two dated, editorially source-attributed national lead registries; never Watch events.
 try{
  const paths=['./data/nationwide-original-source-research-leads-2026-10-29.json',
   './data/nationwide-original-research-leads-expanded-2026-10-29.json'];
  const national=await Promise.all(paths.map(async path=>{
   const response=await win.fetch(path,{cache:'no-store',referrerPolicy:'no-referrer'});
   if(!response.ok)throw Error('National research source HTTP '+response.status);
   return response.json();
  }));
  leads=[...historical,...I.leadFromNational(national)];
 }catch(err){
  $('leadStatus').textContent='Supplemental national research sources withheld: '+err.message+
   '. Existing primary docket remains available.';
 }
 const distinct=[...new Set(leads.map(l=>l.locality_key))].sort();
 for(const key of distinct){for(const id of ['jurisdiction','followJurisdiction']){
  const opt=element('option',key.replace('|',', '));opt.value=key;$(id).append(opt);
 }}
 try{
  if(!win.KATOPTRON_CONFIG?.supabaseUrl||!win.KATOPTRON_CONFIG?.supabasePublishableKey)throw Error('Source feed configuration unavailable');
  const url=win.KATOPTRON_CONFIG.supabaseUrl.replace(/\/$/,'')+
   '/rest/v1/flock_agency_watch_events?select=event_key,locality_key,source_agency_id,kind,title,summary,source_url,source_date,evidence_tier,observed_at&order=observed_at.desc&limit=200';
  const response=await win.fetch(url,{headers:{apikey:win.KATOPTRON_CONFIG.supabasePublishableKey},
   cache:'no-store',referrerPolicy:'no-referrer',signal:AbortSignal.timeout(15000)});
  if(!response.ok)throw Error('Reviewed Watch HTTP '+response.status);
  const rows=await response.json();
  if(!Array.isArray(rows))throw Error('Unexpected reviewed Watch feed');
  leads=[...I.leadFromWatch(rows),...leads];eventsKnown=true;
 }catch(err){
  $('leadStatus').textContent='Watch service unavailable: '+err.message+'. Showing only historically validated government records.';
 }
 // Add jurisdictions sourced only from published Watch events.
 for(const key of [...new Set(leads.map(l=>l.locality_key))].sort()){
  if(distinct.includes(key))continue;
  for(const id of ['jurisdiction','followJurisdiction']){
   const opt=element('option',key.replace('|',', '));opt.value=key;$(id).append(opt);
  }
 }
 const wanted=new URL(win.location.href).searchParams.get('agency');
 const permitted=[...new Set(leads.map(l=>l.locality_key))];
 if(permitted.includes(wanted))$('jurisdiction').value=wanted;
 issues=I.compare(docket);renderLeads();renderGapBacklog();
 choose((permitted.includes(wanted)&&leads.find(l=>l.locality_key===wanted))||leads[0]);
 renderFeed();
 $('evidenceStatus').textContent='Original-government index validated ('+docket.rows.length+' source records, compiled '+compiledOn+'). '+
  (eventsKnown?'Reviewed Watch records loaded separately.':'Watch records unavailable; no fresh claims displayed.');
 optionalVerifiedDiffs();
 auth().catch(e=>{$('feedAuthStatus').textContent='Private feed unavailable: '+e.message;});
}catch(err){
 $('evidenceStatus').textContent='Evidence withheld: '+err.message+'. No leads or research package published without original-source validation.';
 $('downloadPackage').disabled=true;$('printPackage').disabled=true;
}
})(window);
