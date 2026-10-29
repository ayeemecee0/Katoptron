/* Optional product research only; no payments, entitlements or email sent. */
(function(root){
 'use strict';if(!root||!root.document)return;
 root.addEventListener('DOMContentLoaded',async()=>{
  const $=id=>root.document.getElementById(id),cfg=root.KATOPTRON_CONFIG;
  if(!root.supabase||!cfg){$('pilotStatus').textContent='Account connection unavailable';return;}
  const sb=root.supabase.createClient(cfg.supabaseUrl,cfg.supabasePublishableKey);
  const result=await sb.auth.getUser();
  if(result.error||!result.data?.user?.email_confirmed_at){
   $('pilotStatus').textContent='Sign in with a confirmed Katoptron account from the research workspace to participate. No interest response is stored.';
   return;
  }
  const user=result.data.user;$('interest').hidden=false;
  async function load(){
   const {data,error}=await sb.from('research_pilot_interest').select('*').eq('user_id',user.id).maybeSingle();
   if(error){$('pilotStatus').textContent='Private interest status unavailable: '+error.message;return}
   if(!data){$('pilotStatus').textContent='Participation optional. You have not saved a research response.';return;}
   for(const [field,name] of [['pilotRole','professional_role'],['pilotSeats','seats_band'],['pilotValue','willingness_band'],['pilotPriority','top_priority'],['pilotOrg','organization_note']])$(field).value=data[name]||'';
   $('pilotStatus').textContent='Previously saved voluntary response loaded. You may update it or withdraw it.';
  }
  $('interest').addEventListener('submit',async e=>{
   e.preventDefault();
   const values={user_id:user.id,professional_role:$('pilotRole').value,seats_band:$('pilotSeats').value,
    willingness_band:$('pilotValue').value,top_priority:$('pilotPriority').value,
    organization_note:$('pilotOrg').value.trim(),updated_at:new Date().toISOString()};
   const {error}=await sb.from('research_pilot_interest').upsert(values,{onConflict:'user_id'});
   $('pilotStatus').textContent=error?'Response not saved: '+error.message:
    'Voluntary research response saved. No charge or subscription was created.';
  });
  $('withdrawInterest').addEventListener('click',async()=>{
   if(!root.confirm('Permanently erase your voluntary professional pilot response?'))return;
   const {error}=await sb.from('research_pilot_interest').delete().eq('user_id',user.id);
   $('pilotStatus').textContent=error?'Response deletion failed: '+error.message:
    'Your private pilot-interest response was deleted.';
  });
  await load();
 });
})(typeof window!=='undefined'?window:null);
