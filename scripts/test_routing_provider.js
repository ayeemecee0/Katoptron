const assert=require('node:assert/strict');const P=require('../routing-provider.js');
async function main(){
 assert.equal(P.base('https://example.com/'),'https://example.com');
 for(const u of ['http://example.com','https://u:p@example.com','https://example.com/?key=1'])
  assert.throws(()=>P.base(u),/credential-free HTTPS/);
 let seen;
 const c=P.client(async(url,options)=>{seen=options;return new Response('{"ok":true}',{
  headers:{'content-type':'application/json'}})});
 assert.deepEqual(await c.json('routing','https://example.com/route?a=b',4000),{ok:true});
 assert.equal(seen.referrerPolicy,'no-referrer');assert.equal(seen.redirect,'error');
 assert.equal(seen.credentials,'omit');assert.equal(seen.cache,'no-store');
 const limited=P.client(async()=>new Response('limit',{status:429}));
 await assert.rejects(()=>limited.json('geocoding','https://example.com/api',3000),/rate limited/);
 assert.equal(limited.status('geocoding').available,false);
 await assert.rejects(()=>limited.json('geocoding','https://example.com/api',3000),/quota\/rate limit active/);
 let n=0;const transient=P.client(async()=>{n++;return n===1
  ?new Response('temporary',{status:503}):new Response('{"code":"Ok"}',{headers:{'content-type':'application/json'}});},
  ()=>Date.now(),async()=>{});
 assert.equal((await transient.json('routing','https://example.com/route',3000)).code,'Ok');
 assert.equal(n,2);
 const bad=P.client(async()=>new Response('Not JSON',{headers:{'content-type':'application/json'}}));
 await assert.rejects(()=>bad.json('routing','https://example.com/route',3000),/invalid JSON/);
 const large=P.client(async()=>new Response('[]',{headers:{'content-type':'application/json','content-length':'9000000'}}));
 await assert.rejects(()=>large.json('routing','https://example.com/route',3000),/too large/);
 const ac=new AbortController();ac.abort();
 await assert.rejects(()=>c.json('routing','https://example.com/route',3000,ac.signal),e=>e.name==='AbortError');
 // 429 must honor provider Retry-After without retrying or disclosing route URLs.
 let now=100000,attempts=0;
 const quota=P.client(async()=>{
  attempts++;
  return new Response('quota',{status:429,headers:{'retry-after':'120'}});
 },()=>now,async()=>{});
 await assert.rejects(()=>quota.json('routing','https://example.com/route?test=1',4000),
   /rate limited/);
 assert.equal(attempts,1);
 assert.equal(quota.status('routing').reason,'quota');
 assert.equal(quota.status('routing').retryAfterSeconds,120);
 assert.equal(quota.status('geocoding').available,true,'Routing quota must not disable geocoding');
 await assert.rejects(()=>quota.json('routing','https://example.com/route',4000),
   /retry in approximately 120 seconds/);
 assert.equal(attempts,1,'Do not spend provider credits during rate-limit window');
 now+=120000;
 assert.equal(quota.status('routing').available,true);
 // Retry-After is bounded, never permits arbitrary years of disabled service.
 const future=P.client(async()=>new Response('quota',{status:429,
   headers:{'retry-after':'99999999'}}),()=>now,async()=>{});
 await assert.rejects(()=>future.json('routing','https://example.com/route',4000),/rate limited/);
 assert.equal(future.status('routing').retryAfterSeconds,3600);
 console.log('Provider transport, privacy and reliability tests passed');
}
main().catch(e=>{console.error(e);process.exitCode=1;});