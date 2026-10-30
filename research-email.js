/* Separate researcher email consent. Never triggered by saving an in-app follow. */
(function(win){
'use strict';
const $=id=>win.document.getElementById(id);
if(!$('researchEmailEnable'))return;
let client=null,user=null;
const status=msg=>$('researchEmailStatus').textContent=msg;
function choice(){
 const key=$('followJurisdiction').value;
 const topics=[...win.document.querySelectorAll('.followTopic:checked')].map(x=>x.value);
 const keyword=$('researchQuestion').value.trim();
 if(!/^[a-z0-9][a-z0-9 -]{1,120}\|[A-Z]{2}$/.test(key))throw Error('Choose an indexed jurisdiction');
 if(!topics.length||topics.some(t=>!['contract','policy','oversight','sharing','procurement'].includes(t)))
  throw Error('Choose at least one valid topic');
 if(keyword.length>160)throw Error('Research keyword exceeds limit');
 return {locality_key:key,topics,keyword};
}
async function account(){
 if(!win.supabase||!win.KATOPTRON_CONFIG?.supabasePublishableKey)return null;
 client ||= win.supabase.createClient(win.KATOPTRON_CONFIG.supabaseUrl,
  win.KATOPTRON_CONFIG.supabasePublishableKey);
 const {data,error}=await client.auth.getUser();
 if(error&&error.name!=='AuthSessionMissingError')throw Error('Account verification failed');
 user=data?.user||null;return user?.email_confirmed_at?user:null;
}
async function refresh(){
 $('researchEmailReceipts').replaceChildren();
 if(!await account()){status('Research emails OFF or sign-in unavailable. Sign in with a confirmed email account to manage this separate consent.');return}
 const {locality_key}=choice();
 const [pref,claim]=await Promise.all([
  client.from('research_email_subscriptions').select('enabled,opted_in_at,topics,keyword')
   .eq('user_id',user.id).eq('locality_key',locality_key).maybeSingle(),
  client.from('research_email_send_claims').select('event_key,status,claimed_at,smtp_accepted_at')
   .eq('user_id',user.id).eq('locality_key',locality_key).order('claimed_at',{ascending:false}).limit(15)
 ]);
 if(pref.error||claim.error)throw Error('Private consent or send-history query unavailable');
 const sub=pref.data;
 status(sub?.enabled?'ENABLED for '+locality_key+' since '+sub.opted_in_at+
    '; only new matching reviewed government events are eligible.':
    'OFF for '+locality_key+'. In-app follows and Government Watch email preferences are unchanged.');
 if(!claim.data?.length){$('researchEmailReceipts').textContent='No SMTP submissions recorded for this jurisdiction.';return}
 for(const row of claim.data){
  const line=win.document.createElement('p');
  line.textContent='Source event '+row.event_key.slice(0,16)+' · '+(
   row.status==='smtp_submitted'?'SMTP accepted; inbox delivery not confirmed':
   row.status==='uncertain'?'SMTP outcome uncertain; will not automatically resend':
   row.status==='claimed'?'Claimed; SMTP status not confirmed':
   row.status==='canceled'?'Canceled after consent change':
   row.status==='queued'?'Queued, not yet sent':'Status not established');
  $('researchEmailReceipts').append(line);
 }
}
$('researchEmailEnable').addEventListener('click',async()=>{
 try{
  if(!await account())throw Error('Confirmed sign-in is required');
  if(!$('researchEmailConsent').checked)throw Error('Explicit email consent checkbox is required');
  const prefs=choice();
  const prior=await client.from('research_email_subscriptions').select('enabled').eq('user_id',user.id)
   .eq('locality_key',prefs.locality_key).maybeSingle();
  if(prior.error)throw Error('Cannot verify existing email consent');
  const request=prior.data?client.from('research_email_subscriptions').update({topics:prefs.topics,keyword:prefs.keyword,enabled:true})
     .eq('user_id',user.id).eq('locality_key',prefs.locality_key):
    client.from('research_email_subscriptions').insert({...prefs,user_id:user.id});
  const {error}=await request;if(error)throw Error('Consent could not be saved: '+error.message);
  $('researchEmailConsent').checked=false;await refresh();
 }catch(e){status('Research email NOT enabled: '+e.message)}
});
$('researchEmailDisable').addEventListener('click',async()=>{
 try{
  if(!await account())throw Error('Confirmed sign-in required');
  const {locality_key}=choice();
  const {error}=await client.from('research_email_subscriptions').update({enabled:false})
    .eq('user_id',user.id).eq('locality_key',locality_key);
  if(error)throw Error(error.message);
  $('researchEmailConsent').checked=false;await refresh();
 }catch(e){status('Unable to update research email consent: '+e.message)}
});
$('researchEmailRefresh').addEventListener('click',()=>refresh().catch(e=>status(e.message)));
$('followJurisdiction').addEventListener('change',()=>refresh().catch(e=>status(e.message)));
if(win.supabase&&win.KATOPTRON_CONFIG?.supabasePublishableKey){
 client=win.supabase.createClient(win.KATOPTRON_CONFIG.supabaseUrl,
  win.KATOPTRON_CONFIG.supabasePublishableKey);
 client.auth.onAuthStateChange(()=>{win.setTimeout(()=>refresh().catch(e=>status(e.message)),0)});
 refresh().catch(e=>status(e.message));
}
})(window);
