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
  const user=result.data.user;$('interest').hidden=false;$('measurementForm').hidden=false;
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
  async function loadMeasurements(){
   const {data,error}=await sb.from('research_pilot_task_measurements').select('id,task_kind,manual_estimate_minutes,software_minutes,task_completed,recorded_at').eq('user_id',user.id).order('recorded_at',{ascending:false}).limit(100);
   if(error){$('measurementStatus').textContent='Private task measurement unavailable: '+error.message;return;}
   $('measurementStatus').textContent=data.length+' voluntary task measurement(s) stored. Self-reported values are not verified performance measurements.';
  }
  $('measurementForm').addEventListener('submit',async event=>{
   event.preventDefault();
   if(!$('measurementConsent').checked)return;
   const manual=Number($('manualMinutes').value),software=Number($('softwareMinutes').value);
   if(!Number.isInteger(manual)||!Number.isInteger(software)||manual<1||manual>1440||software<1||software>1440){
    $('measurementStatus').textContent='Enter a whole-minute value between 1 and 1440.';return;
   }
   const {error}=await sb.from('research_pilot_task_measurements').insert({
    user_id:user.id,task_kind:$('taskKind').value,manual_estimate_minutes:manual,software_minutes:software,
    task_completed:$('taskCompleted').value==='true'
   });
   if(error){$('measurementStatus').textContent='Measurement not saved: '+error.message;return;}
   $('measurementConsent').checked=false;
   $('manualMinutes').value='';$('softwareMinutes').value='';
   await loadMeasurements();
  });
  $('eraseMeasurements').addEventListener('click',async()=>{
   if(!root.confirm('Erase every optional pilot task measurement stored under your account?'))return;
   const {error}=await sb.from('research_pilot_task_measurements').delete().eq('user_id',user.id);
   if(error){$('measurementStatus').textContent='Deletion failed: '+error.message;return;}
   await loadMeasurements();
  });
  await Promise.all([load(),loadMeasurements()]);
 });
})(typeof window!=='undefined'?window:null);
