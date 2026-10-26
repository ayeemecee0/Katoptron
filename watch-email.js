/* Katoptron verified-account opt-in for new public-source event notifications.
 * Unauthenticated on-device following remains independent of this module.
 * Email subscriptions default OFF; confirmed Auth email is required.
 */
(()=>{
 'use strict';
 const cfg=window.KATOPTRON_CONFIG,$=id=>document.getElementById(id);
 if(!window.supabase||!cfg||!$('watchEmailStatus'))return;
 const client=window.supabase.createClient(cfg.supabaseUrl,cfg.supabasePublishableKey);
 let user=null,locality=null;
 const report=message=>$('watchEmailStatus').textContent=message;
 async function sync(){
  const {data,error}=await client.auth.getUser();
  user=error?null:data?.user;
  $('watchSignout').hidden=!user;
  $('watchSubscribe').disabled=!(user&&locality);
  $('watchUnsubscribe').disabled=!(user&&locality);
  $('watchAuthStatus').textContent=user?
   'Authenticated as '+user.email+'. Your address must be confirmed to send messages.':
   'Sign in to opt in to confirmed-account email notices.';
  if(user&&locality)await refresh();
 }
 async function refresh(){
  if(!user||!locality)return;
  const {data,error}=await client.from('flock_watch_subscriptions')
   .select('email_enabled,watch_government,watch_vendor,watch_sharing,watch_renewals')
   .eq('user_id',user.id).eq('locality_key',locality.key).maybeSingle();
  if(error){report('Subscription status unavailable: '+error.message);return}
  report(data?.email_enabled?
   'Email preference enabled for '+locality.label+'; source-change mail requires an active sender.':
   'Email alerts currently OFF for '+locality.label+'.');
  if(data){$('watchGov').checked=data.watch_government;$('watchVendor').checked=data.watch_vendor;
   $('watchSharing').checked=data.watch_sharing;$('watchRenewal').checked=data.watch_renewals;}
 }
 async function verifiedUser(){
  const {data,error}=await client.auth.getUser();
  if(error||!data?.user||!data.user.email_confirmed_at){
   report('Confirm your account email before opting in.');return null;}
  return data.user;
 }
 $('watchAuth').addEventListener('submit',async e=>{
  e.preventDefault();
  const {error}=await client.auth.signInWithPassword({
   email:$('watchEmail').value.trim(),password:$('watchPassword').value});
  $('watchAuthStatus').textContent=error?'Sign-in unsuccessful: '+error.message:'Signed in.';
  if(!error)await sync();
 });
 $('watchSignup').addEventListener('click',async()=>{
  if(!$('watchEmail').reportValidity()||!$('watchPassword').reportValidity())return;
  const {error}=await client.auth.signUp({
   email:$('watchEmail').value.trim(),password:$('watchPassword').value,
   options:{emailRedirectTo:location.origin+location.pathname}});
  $('watchAuthStatus').textContent=error?'Registration failed: '+error.message:
    'Check your mailbox and confirm your account. No alert subscription has been enabled.';
 });
 $('watchSignout').addEventListener('click',async()=>{
  await client.auth.signOut();await sync();
 });
 $('watchSubscribe').addEventListener('click',async()=>{
  if(!locality)return;
  const verified=await verifiedUser();if(!verified)return;
  const record={
   user_id:verified.id,locality_key:locality.key,email_enabled:true,
   watch_government:$('watchGov').checked,
   watch_vendor:$('watchVendor').checked,
   watch_sharing:$('watchSharing').checked,
   watch_renewals:$('watchRenewal').checked
  };
  if(![record.watch_government,record.watch_vendor,record.watch_sharing,
       record.watch_renewals].some(Boolean)){
    report('Select at least one alert category. No subscription created.');return;
  }
  const {error}=await client.from('flock_watch_subscriptions').upsert(record,{
   onConflict:'user_id,locality_key'});
  report(error?'Subscription unavailable: '+error.message:
   'Email opt-in saved for '+locality.label+
   '. Digests cover newly observed source evidence only and require an active encrypted mail sender.');
 });
 $('watchUnsubscribe').addEventListener('click',async()=>{
  if(!locality||!user)return;
  const {error}=await client.from('flock_watch_subscriptions').delete()
   .eq('user_id',user.id).eq('locality_key',locality.key);
  report(error?'Unable to disable subscription: '+error.message:
   'Email preference disabled and deleted for '+locality.label+'.');
 });
 client.auth.onAuthStateChange(()=>queueMicrotask(sync));
 window.KatoptronWatchMail={select(place){locality=place;void sync()}};
 void sync();
})();
