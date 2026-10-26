const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1150,height:850}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 try{
  // Stub ONLY the third-party Auth client. Test the actual published
  // watch-email.js and page UI, NEVER create real accounts or emails.
  await page.addInitScript(()=>{
   const data=new Map(),events=[];
   let confirmed=false,loggedIn=false;
   const uid='99999999-8888-4777-8aaa-666666666666';
   const record={id:uid,email:'test@example.org',
     email_confirmed_at:'2026-10-25T20:00:00Z'};
   function result(v){return Promise.resolve({data:v,error:null})}
   const client={
    auth:{
      async getUser(){return result({user:loggedIn?{...record,email_confirmed_at:confirmed?record.email_confirmed_at:null}:null})},
      async signInWithPassword(){loggedIn=true;confirmed=true;return result({user:{...record}})},
      async signUp(){loggedIn=false;confirmed=false;return result({user:null})},
      async signOut(){loggedIn=false;return result({user:null})},
      onAuthStateChange(fn){return {data:{subscription:{unsubscribe(){}}}}},
    },
    from(table){
     if(table!=='flock_watch_subscriptions')throw Error('Unexpected table query '+table);
     let key=null;
     const q={
      select(){return this},
      eq(column,val){if(column==='locality_key')key=val;return this},
      async maybeSingle(){return result(data.get(key)||null)},
      async upsert(row){if(!loggedIn||!confirmed)throw Error('Unexpected unconfirmed write');
       data.set(row.locality_key,{...row});events.push({action:'upsert',row});return result(row)},
      delete(){this.deleting=true;return this},
      then(onOk,onErr){if(this.deleting){data.delete(key);events.push({action:'delete',key})}
       return Promise.resolve({data:null,error:null}).then(onOk,onErr)}
     };
     return q;
    }
   };
   Object.defineProperty(window,'supabase',{configurable:true,value:{createClient(){return client}}});
   window.__testWatch={data,events,confirm(){confirmed=true},unconfirm(){confirmed=false},
     login(){loggedIn=true},user(){return loggedIn}};
  });
  // Avoid external CDN unmocking our deliberately isolated client.
  await page.route('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@*/dist/umd/supabase.min.js',
    route=>route.fulfill({status:200,body:'/* browser test provides isolated fake auth */',
      contentType:'application/javascript'}));
  const result=await page.goto(new URL('government-watch.html?place=folsom%7CCA',base).href,{
   waitUntil:'domcontentloaded',timeout:45000});
  assert.equal(result?.status(),200);
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent?.includes('localities loaded')&&
    document.querySelector('#open')?.href.includes('folsom'),null,{timeout:45000});
  assert.equal(await page.locator('#watchSubscribe').isDisabled(),true,
   'Anonymous browser visitors must not email-subscribe');
  await page.locator('#watchEmail').fill('test@example.org');
  await page.locator('#watchPassword').fill('correct-horse-battery-staple');
  await page.locator('#watchSignup').click();
  assert.ok((await page.locator('#watchAuthStatus').textContent()).includes('Confirm'));
  assert.equal(await page.locator('#watchSubscribe').isDisabled(),true,
   'Sign-up alone must not turn alerts on');
  await page.locator('#watchAuth button[type=submit]').click();
  await page.waitForFunction(()=>!document.querySelector('#watchSubscribe').disabled);
  await page.evaluate(()=>window.__testWatch.unconfirm());
  await page.locator('#watchSubscribe').click();
  assert.ok((await page.locator('#watchEmailStatus').textContent()).includes('Confirm'));
  assert.equal(await page.evaluate(()=>window.__testWatch.events.length),0,
   'Unconfirmed mailbox must not get enrolled');
  await page.evaluate(()=>window.__testWatch.confirm());
  await page.locator('#watchSharing').uncheck();
  await page.locator('#watchSubscribe').click();
  await page.waitForFunction(()=>document.querySelector('#watchEmailStatus')?.textContent?.includes('opt-in saved'));
  const saved=await page.evaluate(()=>window.__testWatch.data.get('folsom|CA'));
  assert.ok(saved?.email_enabled);
  assert.equal(saved.watch_sharing,false,'Sharing preference was lost');
  assert.equal(saved.watch_government,true);
  await page.locator('#watchUnsubscribe').click();
  await page.waitForFunction(()=>document.querySelector('#watchEmailStatus')?.textContent?.includes('disabled and deleted'));
  assert.equal(await page.evaluate(()=>window.__testWatch.data.size),0);
  assert.deepEqual(await page.evaluate(()=>window.__testWatch.events.map(e=>e.action)),
    ['upsert','delete']);
  assert.deepEqual(errors,[]);
  console.log('GOVERNMENT WATCH OPT-IN PASS: no anonymous or unconfirmed signup, explicit category consent, verified save and deletion, no actual email sent');
 }catch(error){console.error('GOVERNMENT WATCH OPT-IN FAILED:',error.stack||error);console.error(errors);process.exitCode=1}
 finally{await browser.close()}
})().catch(e=>{console.error('Watch browser test harness failed:',e);process.exitCode=1});
