/* Government Watch account UX regression without network access or production writes. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const code=fs.readFileSync(path.join(__dirname,'../watch-email.js'),'utf8');
const html=fs.readFileSync(path.join(__dirname,'../government-watch.html'),'utf8');
for(const id of ['watchSelectionStatus','watchResetForm','watchNewPassword','watchForgot']){
 assert.match(html,new RegExp('id="'+id+'"'),'Missing watch auth control '+id);
}
async function scenario(confirmed){
 let active={id:'example-user',email:'test@example.org',email_confirmed_at:confirmed?'2026-10-25T00:00:00Z':null};
 const nodes=new Map(), calls=[];
 const node=(id)=>{
  if(!nodes.has(id))nodes.set(id,{
   textContent:'',value:'',disabled:false,hidden:false,checked:false,
   listeners:{},reportValidity(){return true},
   addEventListener(name,callback){this.listeners[name]=callback;}
  });
  return nodes.get(id);
 };
 const sub=()=>{
  const eq2={maybeSingle:async()=>({data:null,error:null})};
  const eq1={eq:()=>eq2};
  return {
   select:()=>({eq:()=>eq1}),
   delete:()=>({eq:()=>({eq:async()=>({error:null})})}),
   upsert:async()=>({error:null})
  };
 };
 let onAuth=null;
 const auth={
  getUser:async()=>({data:{user:active},error:null}),
  onAuthStateChange(cb){onAuth=cb},
  signUp:async(args)=>{calls.push(['signUp',args.email]);return {data:{},error:null}},
  signInWithPassword:async()=>({error:null}),
  resetPasswordForEmail:async()=>({error:null}),
  updateUser:async()=>({error:null}),
  signOut:async()=>{active=null;return {error:null}}
 };
 const window={
  KATOPTRON_CONFIG:{supabaseUrl:'https://example.test',supabasePublishableKey:'fake'},
  supabase:{createClient:()=>({auth,from:()=>sub()})}
 };
 const context={window,document:{getElementById:node},
  location:{origin:'https://example.test',pathname:'/government-watch.html'},
  queueMicrotask:(cb)=>Promise.resolve().then(cb)};
 vm.runInNewContext(code,context,{timeout:2000});
 const settle=async()=>{for(let i=0;i<6;i++)await Promise.resolve()};
 await settle();
 assert.equal(node('watchUnsubscribe').disabled,true);
 assert.equal(node('watchSubscribe').disabled,true);
 assert.match(node('watchSelectionStatus').textContent,/No locality selected/);
 assert.match(node('watchAuthStatus').textContent,confirmed?/Email confirmed/:/Email not confirmed/);
 window.KatoptronWatchMail.select({key:'moline|IL',label:'Moline, IL'});
 await settle();
 assert.equal(node('watchUnsubscribe').disabled,false,'Unsubscribe must work for signed-in users, including unconfirmed accounts');
 assert.equal(node('watchSubscribe').disabled,!confirmed);
 assert.match(node('watchSelectionStatus').textContent,/Moline, IL/);
 node('watchEmail').value='test@example.org';
 node('watchPassword').value='not-real-password';
 await node('watchSignup').listeners.click();
 assert.match(node('watchAuthStatus').textContent,/If this address is new/);
 assert.match(node('watchAuthStatus').textContent,/already have an account/);
 await node('watchForgot').listeners.click();
 assert.match(node('watchAuthStatus').textContent,/reset link may arrive/);
 onAuth('PASSWORD_RECOVERY');
 assert.equal(node('watchResetForm').hidden,false);
 window.KatoptronWatchMail.select(null);
 await settle();
 assert.equal(node('watchUnsubscribe').disabled,true);
 assert.equal(node('watchSubscribe').disabled,true);
 return calls;
}
(async()=>{
 await scenario(true);
 await scenario(false);
 console.log('PHASE3_WATCH_AUTH_UI_PASS: real confirmed status, locality selection, disabled controls, generic repeat signup, reset request, recovery form');
})().catch(e=>{console.error(e);process.exitCode=1});
