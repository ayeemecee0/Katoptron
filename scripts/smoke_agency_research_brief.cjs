const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1180,height:850}});
 const problems=[];page.on('pageerror',e=>problems.push(e.message));
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 try{
   let r=await page.goto(new URL('agency-xray.html?place=folsom%7CCA',base).href,
       {waitUntil:'domcontentloaded',timeout:40000});
   assert.equal(r?.status(),200);
   await page.waitForFunction(()=>document.querySelector('#profileTitle')
       ?.textContent?.includes('Folsom'),null,{timeout:40000});
   const link=await page.locator('#brief').getAttribute('href');
   assert.ok(link.includes('agency-brief.html?place='));
   r=await page.goto(new URL(link,base).href,{waitUntil:'domcontentloaded',timeout:40000});
   assert.equal(r?.status(),200);
   await page.waitForFunction(()=>document.querySelector('#status')
     ?.textContent?.includes('printable report ready'),null,{timeout:45000});
   assert.ok((await page.locator('#title').textContent()).includes('Folsom'));
   assert.equal(await page.locator('#print').isDisabled(),false);
   assert.ok((await page.locator('#counts').textContent()).includes('original Flock vendor snapshots'));
   const original=await page.locator('#firstParty a').first().getAttribute('href');
   assert.ok(original?.startsWith('https://transparency.flocksafety.com/'));
   assert.ok((await page.locator('#identity').textContent()).includes('Establishes portal identity only'));
   const gaps=await page.locator('#gaps li').allTextContents();
   assert.ok(gaps.some(x=>x.includes('Current data-sharing permissions')));
   assert.ok((await page.locator('#content').textContent()).includes('secondary'));
   assert.ok(!(await page.locator('#counts').textContent()).includes('0 verified cameras'),
      'Unknown never becomes a declaration of zero Flock installed cameras');
   r=await page.goto(new URL('agency-brief.html?place=nonexistent%7CZZ',base).href,
     {waitUntil:'domcontentloaded',timeout:25000});
   await page.waitForFunction(()=>document.querySelector('#status')
     ?.textContent?.includes('No source-qualified published dossier'),null,{timeout:45000});
   assert.equal(await page.locator('#print').isDisabled(),true,
       'Unsupported municipality must not produce speculative PDF');
   assert.deepEqual(problems,[]);
   console.log('AGENCY BRIEF PASS: source-cited Folsom dossier printable with tiers and unknowns; nonexistent source blocked');
 }catch(e){console.error('AGENCY BRIEF FAILED:',e.stack||e);console.error(problems);process.exitCode=1}
 finally{await browser.close()}
})().catch(e=>{console.error('Agency brief browser harness failed:',e);process.exitCode=1});
