/* Simulated authenticated browser lifecycle with a local fake Supabase client.
 * It verifies frontend wiring, NOT real Supabase email confirmation, RLS, or Storage.
 * Real authorization is separately tested using rollback-only Postgres integration.
 */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const mockSdk=String.raw`
(()=>{
'use strict';
const reviewerMode=location.pathname.includes('community-review.html');
const followupMode=location.search.includes('scenario=followup');
const staleMode=location.search.includes('scenario=stale');
const retryMode=location.search.includes('scenario=retrydelete');
const recoveryMode=location.search.includes('scenario=recovery');
const contributor={id:'11111111-aaaa-4111-8111-111111111111',email:'qa.contributor@example.invalid'};
const reviewer={id:'22222222-bbbb-4222-8222-222222222222',email:'qa.reviewer@example.invalid'};
const id='33333333-cccc-4333-8333-333333333333';
let session=(staleMode||recoveryMode)?{user:reviewerMode?reviewer:contributor}:null;
const onAuth=[];
const reports=reviewerMode?
 [{submission_id:id,created_at:'2026-10-23T12:00:00Z',latitude:38.5,longitude:-121.5,
   description:'This mock report exists only to test private review UI handling.',
   report_status:'pending',screening_state:'review_needed',
   related_submission_count:0,matching_verified_count:0,
   original_source_url:'https://example.org/mock-review-proof'}]:
 followupMode?
 [{submission_id:id,created_at:'2026-10-23T12:00:00Z',
   report_status:'needs_evidence',observed_on:null}]:
 retryMode?
 [{submission_id:id,created_at:'2026-10-23T12:00:00Z',
   report_status:'withdrawn',observed_on:null}]:[];
const activity={uploaded:[],deleted:[],signed:[],reviewed:[],withdrawn:[],erased:[],lastSubmission:null,deleteAttempts:0,resetRequests:[],passwordUpdates:[]};
function signal(){for(const cb of onAuth)cb('SIGNED_IN',session);}
const auth={
 getSession:async()=>({data:{session},error:null}),
 getUser:async()=>staleMode?
   ({data:{user:null},error:{message:'Mock Auth server rejects expired cached token'}}):
   ({data:{user:session?.user||null},error:null}),
 signInWithPassword:async({email})=>{
   session={user:reviewerMode?reviewer:{...contributor,email}};
   signal();return{data:{session},error:null};
 },
 signUp:async()=>({data:{user:contributor,session:null},error:null}),
 resetPasswordForEmail:async(email,options)=>{
   activity.resetRequests.push({email,options});return{data:{},error:null};
 },
 updateUser:async({password})=>{
   activity.passwordUpdates.push(password);return{data:{user:session?.user},error:null};
 },
 signOut:async()=>{session=null;signal();return{error:null}},
 onAuthStateChange:callback=>{
   onAuth.push(callback);
   if(recoveryMode)queueMicrotask(()=>callback('PASSWORD_RECOVERY',session));
   return{data:{subscription:{unsubscribe(){}}}};
 }
};
const api={
 auth,
 from(table){
   if(table!=='flock_community_submissions')throw Error('Unexpected fake table: '+table);
   return {
     select:()=>({order:()=>({limit:async()=>({data:reports,error:null})})}),
     update:patch=>({eq:(field,value)=>({select:async()=>{
       const match=reports.find(r=>r[field]===value&&
         ['pending','needs_evidence'].includes(r.report_status)&&!r.original_source_url);
       if(!match)return{data:[],error:null};
       match.original_source_url=patch.original_source_url;
       return{data:[{submission_id:match.submission_id}],error:null};
     }})}),
     insert:row=>({select:()=>({single:async()=>{
       const record={...row,submission_id:id,created_at:'2026-10-23T12:00:00Z',report_status:'pending'};
       reports.push(record);activity.lastSubmission=record;
       return{data:{submission_id:id},error:null};
     }})})
   };
 },
 async rpc(name,args){
   if(name==='withdraw_own_community_report'){
     reports.find(r=>r.submission_id===args.p_id).report_status='withdrawn';
     activity.withdrawn.push(args.p_id);return{data:true,error:null};
   }
   if(name==='delete_withdrawn_community_report'){
     const r=reports.find(x=>x.submission_id===args.p_id);
     if(!r)return{data:false,error:null};
     if(r.report_status!=='withdrawn'||!activity.deleted.length)
       return{data:null,error:{message:'Remove photo before erasure'}};
     reports.splice(reports.indexOf(r),1);
     activity.erased.push(args.p_id);return{data:true,error:null};
   }
   if(name==='list_community_review_queue'){
     return{data:reports.filter(x=>['pending','needs_evidence'].includes(x.report_status)),error:null};
   }
   if(name==='community_report_attachment_paths'){
     return{data:[{object_path:contributor.id+'/'+id+'/evidence.webp'}],error:null};
   }
   if(name==='set_community_review_status'){
     reports.find(r=>r.submission_id===args.p_id).report_status=args.p_status;
     activity.reviewed.push(args);return{data:null,error:null};
   }
   throw Error('Unexpected fake RPC: '+name);
 },
 storage:{
  from(bucket){
   if(bucket!=='katoptron-community-evidence')throw Error('Unexpected bucket');
   return{
    upload:async(path,file,options)=>{
      activity.uploaded.push({path,size:file.size,mime:file.type,options});return{data:{path},error:null};
    },
    list:async()=>({data:activity.deleted.length?[]:[{name:'evidence.webp'}],error:null}),
    remove:async(paths)=>{
      activity.deleteAttempts++;
      if(retryMode&&activity.deleteAttempts===1)
        return{data:null,error:{message:'Synthetic temporary network interruption'}};
      activity.deleted.push(...paths);return{data:paths,error:null};
    },
    createSignedUrl:async(path,seconds)=>{
      activity.signed.push({path,seconds});
      return{data:{signedUrl:'https://example.invalid/private-photo?mock=1'},error:null};
    }
   };
  }
 }
};
window.supabase={createClient:()=>api};
window.__QA={reports,activity};
})();`;
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 try{
   const page=await browser.newPage({viewport:{width:1150,height:900}});
   await page.route('**/supabase.min.js',route=>route.fulfill({
     status:200,contentType:'application/javascript',body:mockSdk
   }));
   page.on('dialog',dialog=>dialog.accept());
   const first=await page.goto(new URL('submit.html',base).href,{waitUntil:'load'});
   assert.equal(first.status(),200);
   assert.equal(await page.locator('#reportPanel').isHidden(),true);
   await page.locator('#email').fill('qa.contributor@example.invalid');
   await page.locator('#password').fill('eightchars');
   await page.locator('#register').click();
   assert.ok((await page.locator('#notice').textContent()).includes('at least 12 characters'),
     'Signup must explain the stronger new-account password requirement');
   await page.locator('#password').fill('another-safe-mock-password');
   await page.locator('#register').click();
   assert.ok((await page.locator('#notice').textContent()).includes('verification link'),
     'Pending confirmation must display a usable verification instruction');
   assert.equal(await page.locator('#reportPanel').isHidden(),true,
     'No account session may open private contribution');
   console.log('MOCK SIGNUP UX PASS: 12-character warning, pending confirmation, no false login');
   await page.locator('#forgotPassword').click();
   await page.waitForFunction(()=>window.__QA.activity.resetRequests.length===1,undefined,{timeout:12000});
   const reset=await page.evaluate(()=>window.__QA.activity.resetRequests[0]);
   assert.equal(reset.email,'qa.contributor@example.invalid');
   assert.equal(new URL(reset.options.redirectTo).pathname,new URL('submit.html',base).pathname,
     'Recovery link must return to the known contributor page');
   assert.equal(new URL(reset.options.redirectTo).origin,new URL(base).origin);
   assert.match(await page.locator('#notice').textContent(),/If an account exists/,
     'Recovery request response should not reveal account existence');
   console.log('MOCK RESET REQUEST PASS: no old password required, fixed redirect and enumeration-safe response');
   await page.locator('#authForm button[type=submit]').click();
   await page.locator('#reportPanel').waitFor({state:'visible',timeout:12000});
   // Camera coordinates are accepted as one local-only comma-separated pair,
   // with no map lookup or third-party geocoder request.
   await page.locator('#coordinates').fill('38.5 -121.5');
   await page.locator('#applyCoordinates').click();
   assert.ok((await page.locator('#coordinateHelp').textContent()).includes('separated by a comma'));
   assert.equal(await page.locator('#lat').inputValue(),'');
   await page.locator('#coordinates').fill('81, -121.5');
   await page.locator('#applyCoordinates').click();
   assert.ok((await page.locator('#coordinateHelp').textContent()).includes('supported U.S. bounds'));
   await page.locator('#coordinates').fill('38.5, -121.5');
   await page.locator('#applyCoordinates').click();
   assert.equal(await page.locator('#lat').inputValue(),'38.5');
   assert.equal(await page.locator('#lon').inputValue(),'-121.5');
   await page.locator('#description').fill(
     'This intentionally fictional QA camera report tests private evidence intake and does not represent a real device.');
   await page.locator('#source').fill('https://example.org/mock-review-proof');
   const png=Buffer.from(await page.evaluate(()=>{
     const canvas=document.createElement('canvas');canvas.width=2;canvas.height=2;
     canvas.getContext('2d').fillRect(0,0,2,2);
     return canvas.toDataURL('image/png').split(',')[1];
   }),'base64');
   await page.locator('#photo').setInputFiles({name:'mock.png',mimeType:'image/png',buffer:png});
   await page.locator('#consent').check();
   await page.locator('#send').click();
   await page.waitForFunction(()=>!!window.__QA?.activity?.uploaded?.length ||
      /Submission not accepted/.test(document.querySelector('#notice')?.textContent||''),
      undefined,{timeout:12000});
   if(!await page.evaluate(()=>!!window.__QA.activity.uploaded.length))
      throw Error('Photo submission failed: '+await page.locator('#notice').textContent());
   const sent=await page.evaluate(()=>window.__QA.activity);
   assert.equal(sent.lastSubmission.publication_consent,false,
     'A new reporter should not consent to publication by default');
   assert.equal(sent.uploaded[0].mime,'image/webp','Image metadata must be discarded by canvas re-encoding');
   assert.equal(sent.uploaded[0].options.upsert,false);
   assert.ok(sent.uploaded[0].path.endsWith('/'+
     '33333333-cccc-4333-8333-333333333333/evidence.webp'));
   await page.getByRole('button',{name:/Withdraw private report/}).click();
   await page.waitForFunction(()=>window.__QA.activity.withdrawn.length===1,undefined,{timeout:12000});
   const withdrawn=await page.evaluate(()=>window.__QA.activity);
   assert.equal(withdrawn.deleted.length,1,'Withdrawn contributor evidence should be removed');
   assert.equal((await page.locator('#myReports').textContent()).includes('withdrawn'),true);
   assert.equal(await page.getByRole('button',{name:/Retry private photo deletion/}).count(),1,
      'Withdrawn contributor must retain ability to retry photo cleanup');
   const eraseBtn=page.getByRole('button',{name:/Permanently erase report/});
   assert.equal(await eraseBtn.count(),1);
   await eraseBtn.click();
   await page.waitForFunction(()=>window.__QA.activity.erased.length===1,undefined,{timeout:12000});
   assert.equal(await page.evaluate(()=>window.__QA.reports.length),0);
   assert.ok((await page.locator('#notice').textContent()).includes('permanently erased'));
   console.log('MOCK CONTRIBUTOR PASS: sign-in, photo, withdrawal, private Storage delete and permanent report erasure');
   await page.goto(new URL('submit.html?scenario=retrydelete',base).href,{waitUntil:'load'});
   await page.locator('#email').fill('qa.contributor@example.invalid');
   await page.locator('#password').fill('another-safe-mock-password');
   await page.locator('#authForm button[type=submit]').click();
   await page.locator('#reportPanel').waitFor({state:'visible',timeout:12000});
   const cleanup=page.getByRole('button',{name:/Retry private photo deletion/});
   await cleanup.click();
   await page.waitForFunction(()=>/Could not confirm photo deletion/.test(
      document.querySelector('#notice')?.textContent||''),undefined,{timeout:12000});
   assert.equal(await page.evaluate(()=>window.__QA.activity.deleted.length),0,
      'A failed private Storage deletion must never be reported as successful');
   await cleanup.click();
   await page.waitForFunction(()=>/Private photo deletion confirmed/.test(
      document.querySelector('#notice')?.textContent||''),undefined,{timeout:12000});
   assert.equal(await page.evaluate(()=>window.__QA.activity.deleted.length),1);
   await cleanup.click();
   await page.waitForFunction(()=>/No private photos remain/.test(
      document.querySelector('#notice')?.textContent||''),undefined,{timeout:12000});
   await page.getByRole('button',{name:/Permanently erase report/}).click();
   await page.waitForFunction(()=>window.__QA.activity.erased.length===1,undefined,{timeout:12000});
   assert.equal(await page.evaluate(()=>window.__QA.reports.length),0);
   console.log('MOCK PHOTO CLEANUP RETRY PASS: real photo cleanup is prerequisite for final erasure');
   await page.goto(new URL('submit.html?scenario=followup',base).href,{waitUntil:'load'});
   await page.locator('#email').fill('qa.contributor@example.invalid');
   await page.locator('#password').fill('another-safe-mock-password');
   await page.locator('#authForm button[type=submit]').click();
   await page.locator('#reportPanel').waitFor({state:'visible',timeout:12000});
   await page.locator('#myReports input[type=url]').fill('https://example.org/original-citation');
   await page.getByRole('button',{name:'Add missing source link'}).click();
   await page.waitForFunction(()=>window.__QA.reports[0].original_source_url==='https://example.org/original-citation',
     undefined,{timeout:12000});
   await page.locator('#myReports input[type=file]').setInputFiles({name:'followup.png',mimeType:'image/png',buffer:png});
   await page.getByRole('button',{name:'Add requested photo'}).click();
   await page.waitForFunction(()=>window.__QA.activity.uploaded.length===1 ||
     /Photo attachment failed/.test(document.querySelector('#notice')?.textContent||''),undefined,{timeout:12000});
   if(!await page.evaluate(()=>window.__QA.activity.uploaded.length))
     throw Error('Followup photo failed: '+await page.locator('#notice').textContent());
   assert.equal(await page.evaluate(()=>window.__QA.reports.length),1,
     'Adding evidence should not create another report or consume a report slot');
   console.log('MOCK FOLLOWUP PASS: missing original source and requested photo both attach without duplicate submission');
   await page.goto(new URL('community-review.html',base).href,{waitUntil:'load'});
   assert.equal(await page.locator('#workspace').isHidden(),true);
   await page.locator('#email').fill('qa.reviewer@example.invalid');
   await page.locator('#password').fill('another-safe-mock-password');
   await page.locator('#login button').click();
   await page.locator('#workspace').waitFor({state:'visible',timeout:12000});
   assert.equal(await page.locator('#cases article').count(),1);
   const rationale=page.locator('#cases textarea');
   assert.match(await rationale.getAttribute('aria-label'),/Required evidence assessment.*report /,
     'Each private reviewer rationale must have a report-specific accessible name');
   assert.equal(await rationale.getAttribute('aria-required'),'true');
   await page.getByRole('button',{name:'Reject'}).click();
   assert.equal(await rationale.getAttribute('aria-invalid'),'true',
     'Missing rationale must expose invalid field to assistive technologies');
   assert.equal(await page.evaluate(()=>document.activeElement?.tagName),'TEXTAREA',
     'Failed moderation should focus the corrective rationale field');
   assert.match(await page.locator('#notice').textContent(),/at least 15 characters/);
   await page.locator('#cases button').first().click();
   await page.waitForFunction(()=>window.__QA.activity.signed.length===1,undefined,{timeout:12000});
   assert.equal(await page.evaluate(()=>window.__QA.activity.signed[0].seconds),60,
      'Reviewer photo links must expire within one minute');
   await page.locator('#cases textarea').fill(
      'This is a deliberately fictional QA reviewer assessment with an original source URL.');
   assert.equal(await rationale.getAttribute('aria-invalid'),null,
     'Corrected reviewer rationale must clear stale invalid state');
   await page.getByRole('button',{name:'Reject'}).click();
   await page.waitForFunction(()=>window.__QA.activity.reviewed.length===1,undefined,{timeout:12000});
   const reviewed=await page.evaluate(()=>window.__QA.activity.reviewed[0]);
   assert.equal(reviewed.p_status,'rejected');
   assert.ok(reviewed.p_note.length>=15,'Reviewer audit rationale was omitted');
   console.log('MOCK REVIEWER PASS: restricted portal gateway, private photo link, mandatory review explanation and decision');
   await page.goto(new URL('submit.html?scenario=stale',base).href,{waitUntil:'load'});
   await page.waitForFunction(()=>
     /saved session could not be verified/i.test(document.querySelector('#notice')?.textContent||''),
     undefined,{timeout:12000});
   assert.equal(await page.locator('#reportPanel').isHidden(),true,
      'Cached stale contributor token must not open private form');
   assert.equal(await page.locator('#authPanel').isVisible(),true);
   await page.goto(new URL('community-review.html?scenario=stale',base).href,{waitUntil:'load'});
   await page.waitForFunction(()=>
     /saved session could not be verified/i.test(document.querySelector('#notice')?.textContent||''),
     undefined,{timeout:12000});
   assert.equal(await page.locator('#workspace').isHidden(),true,
      'Cached stale reviewer token must not open private review queue');
   console.log('STALE SESSION PASS: unverified cached browser token never opens contributor or reviewer pages');
   await page.goto(new URL('submit.html?scenario=recovery',base).href,{waitUntil:'load'});
   await page.locator('#recoveryPanel').waitFor({state:'visible',timeout:12000});
   assert.equal(await page.locator('#authPanel').isHidden(),true);
   assert.equal(await page.evaluate(()=>document.activeElement?.id),'newPassword',
     'Recovery form must place keyboard focus on the new password field');
   assert.equal(await page.locator('#newPassword').getAttribute('aria-describedby'),
     'recoveryPasswordRequirements','Recovery password rules need a programmatic description');
   assert.equal(await page.locator('#reportPanel').isHidden(),true,
     'Recovery must complete password update before private reports appear');
   await page.locator('#newPassword').fill('123456789012-safe');
   await page.locator('#confirmNewPassword').fill('does-not-match-this');
   await page.locator('#saveNewPassword').click();
   assert.match(await page.locator('#notice').textContent(),/must match/);
   assert.equal(await page.locator('#confirmNewPassword').getAttribute('aria-invalid'),'true',
     'Recovery mismatch must expose invalid state to assistive technology');
   assert.equal(await page.evaluate(()=>document.activeElement?.id),'confirmNewPassword',
     'Keyboard focus must go to the invalid confirmation field');
   assert.equal(await page.evaluate(()=>window.__QA.activity.passwordUpdates.length),0);
   await page.locator('#confirmNewPassword').fill('123456789012-safe');
   await page.locator('#saveNewPassword').click();
   await page.waitForFunction(()=>window.__QA.activity.passwordUpdates.length===1,undefined,{timeout:12000});
   assert.equal(await page.evaluate(()=>window.__QA.activity.passwordUpdates[0]),'123456789012-safe');
   await page.locator('#reportPanel').waitFor({state:'visible',timeout:12000});
   assert.equal(await page.locator('#recoveryPanel').isHidden(),true);
   assert.equal(await page.locator('#newPassword').inputValue(),'',
     'New password inputs must be cleared after success');
   console.log('MOCK PASSWORD RECOVERY PASS: recovery event, mismatch rejection, update and safe contributor reentry');
 }catch(err){console.error('MOCK AUTHENTICATED FLOW FAIL:',err.stack||err);process.exitCode=1;}
 finally{await browser.close();}
})().catch(err=>{console.error('Smoke harness failed',err);process.exitCode=1});
