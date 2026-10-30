'use strict';
/* End-to-end public-first pilot flow. No production accounts, case data or
 * service-role credentials are used. Private UI uses a verified-user test
 * double; actual authorization remains separately tested against PostgreSQL. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const context=await browser.newContext({acceptDownloads:true,viewport:{width:1360,height:900}});
 const page=await context.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 try{
  await page.route('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.118.0/dist/umd/supabase.min.js',
   route=>route.fulfill({status:200,contentType:'application/javascript',
    body:fs.readFileSync(path.join(__dirname,'pilot_test_supabase_mock.js'),'utf8')}));
  const first=await page.goto(new URL('pilot-dossiers.html?dossier=sacramento',base).href,
   {waitUntil:'domcontentloaded',timeout:30000});
  assert.equal(first.status(),200);
  await page.locator('#detail').waitFor({state:'visible',timeout:15000});
  assert.match(await page.locator('#loadStatus').textContent(),/ready/);
  assert.match(await page.locator('#dossierTitle').textContent(),/Sacramento/);
  assert.equal(await page.locator('#sourceList article').count(),3);
  assert.equal(await page.locator('#sourceList a').count(),3);
  assert((await page.locator('#questions li').count())>=3);
  assert.equal(await page.locator('#dossierList .card').count(),8);
  const publicDownload=page.waitForEvent('download');
  await page.locator('#downloadBrief').click();
  const brief=await publicDownload;
  const content=fs.readFileSync(await brief.path(),'utf8');
  assert.match(content,/California Office of Land Use/);
  assert.match(content,/2016-04/);
  assert.match(content,/2025-05-29/);
  assert.match(content,/https:\/\/ceqanet.lci.ca.gov\/2025051277/);
  assert.match(content,/not a live camera census/);
  assert.equal((content.match(/<h2>\[/g)||[]).length,3);
  // The first research result is usable before authentication.
  const href=await page.locator('#importLink').getAttribute('href');
  assert(href.includes('dossier=sacramento'));
  await page.locator('#importLink').click();
  await page.locator('#pilotStart').waitFor({state:'visible',timeout:25000});
  await page.waitForFunction(()=>document.querySelector('#pilotAgency')?.value==='sacramento',null,{timeout:15000});
  assert.equal(await page.locator('#pilotAgency').inputValue(),'sacramento');
  await page.locator('#pilotStart').click();
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent?.startsWith('Verified import:'),null,{timeout:22000});
  const result=await page.evaluate(()=>{
   const db=window.__pilotTestTables;
   return {workspaces:db.research_workspaces.length,cases:db.research_cases.length,
    notes:db.research_case_notes.map(x=>({url:x.source_url,note:x.note})),
    requests:db.research_case_requests.map(x=>({status:x.status,body:x.body})),
    files:db.research_case_files.length
   };
  });
  assert.equal(result.workspaces,1);
  assert.equal(result.cases,1);
  assert.equal(result.notes.length,3);
  assert.equal(result.requests.length,1);
  assert.equal(result.requests[0].status,'draft');
  assert.match(result.requests[0].body,/do not request private license-plate observations/i);
  for(const row of result.notes){
   assert.match(row.url,/^https:\/\//);
   assert.match(row.note,/Source status:/);
   assert.match(row.note,/Unresolved questions:/);
   assert(row.note.includes(row.url));
  }
  assert.equal(result.files,0);
  const privateDownload=page.waitForEvent('download');
  await page.locator('#exportBrief').click();
  const caseBrief=fs.readFileSync(await (await privateDownload).path(),'utf8');
  for(const row of result.notes)assert(caseBrief.includes(row.url.replace(/&/g,'&amp;')));
  assert.match(caseBrief,/NOT independently verified/);
  assert.deepEqual(errors,[]);
  console.log('PILOT_FIRST_VALUE_BROWSER_PASS: no-signup government finding + full original brief + three private cited notes + one unsent draft + private case export');
 }catch(e){
  console.error('PILOT_FIRST_VALUE_BROWSER_FAILED:',e.stack||e.message);
  console.error('PAGE_STATUS:',await page.locator('#status').textContent().catch(()=>'?'),
    'QUICKSTART:',await page.locator('#pilotQuickstartStatus').textContent().catch(()=>'?'),
    'BROWSER_ERRORS:',errors.slice(0,5));
  process.exitCode=1;
 }finally{await browser.close()}
})().catch(err=>{console.error(err);process.exitCode=1});
