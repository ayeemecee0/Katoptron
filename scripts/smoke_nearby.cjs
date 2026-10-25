/* Public-source browser proof for staged/fully-published near-coordinate OSM audit.
 * Search and pagination are read-only; no identified person or plate data.
 */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1280,height:900}});
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 const errors=[];page.on('pageerror',err=>errors.push(err.message));
 try{
  const r=await page.goto(new URL('nearby.html',base).href,{waitUntil:'domcontentloaded',timeout:45000});
  assert.equal(r?.status(),200);
  await page.waitForFunction(()=>Number((document.querySelector('#pairCount')?.textContent||'').replaceAll(',',''))>1000,
   null,{timeout:45000});
  const total=Number((await page.locator('#pairCount').textContent()).replaceAll(',',''));
  const small=Number((await page.locator('#shortCount').textContent()).replaceAll(',',''));
  const large=Number((await page.locator('#longCount').textContent()).replaceAll(',',''));
  assert.equal(small+large,total,'Public published source distance bins must reconcile');
  assert.ok((await page.locator('#snapshotStatus').textContent()).includes('Completed'));
  await page.waitForFunction(()=>{
   const s=document.querySelector('#resultStatus')?.textContent||'';
   return s.includes('source-pair result')||s.includes('unavailable');
  },null,{timeout:45000});
  assert.ok((await page.locator('#resultStatus').textContent()).includes('source-pair result'));
  assert.equal(await page.locator('#results tr').count(),30);
  const first=await page.locator('#results tr').first().locator('td').first().innerText();
  assert.match(first,/^(node|way)\/[1-9][0-9]+$/);
  assert.ok((await page.locator('#results tr').first().locator('td').first().locator('a').getAttribute('href')).endsWith(first));
  await page.locator('#next').click();
  await page.waitForFunction(()=>document.querySelector('#pagination')?.textContent?.includes('Page 2'),
   null,{timeout:16000});
  assert.equal(await page.locator('#results tr').count(),30);
  await page.locator('#osmKey').fill(first);
  await page.locator('#filterForm button[type="submit"]').click();
  await page.waitForFunction(()=>document.querySelector('#resultStatus')?.textContent?.includes('source-pair result'),
   null,{timeout:20000});
  const all=await page.locator('#results tr').allTextContents();
  assert.ok(all.length>0&&all.every(x=>x.includes(first)),
    'Exact OSM source lookup returned other source IDs');
  await page.locator('#osmKey').fill('');
  await page.locator('#distanceBand').selectOption('near');
  await page.locator('#filterForm button[type="submit"]').click();
  await page.waitForFunction(()=>document.querySelector('#resultStatus')?.textContent?.includes('source-pair result'),
   null,{timeout:20000});
  for(const s of await page.locator('#results tr td:nth-child(3)').allTextContents()){
   assert.ok(parseFloat(s)<=5,'Distance band filtering not applied');
  }
  assert.deepEqual(errors,[]);
  console.log('NATIONWIDE PERSISTENT OSM NEARBY SEARCH PASS: '+total+' published possible pairs, fully read-only and ODbL-linked');
 }catch(err){console.error('NATIONWIDE PERSISTENT OSM NEARBY SEARCH FAILED:',err.message);process.exitCode=1}
 finally{await browser.close()}
})().catch(e=>{console.error(e.message);process.exitCode=1});
