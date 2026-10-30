'use strict';
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1280,height:900},acceptDownloads:true});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 try{
  const mock=[
   'window.__testFollows=[];',
   'window.supabase={createClient:()=>({',
   'auth:{getUser:async()=>({data:{user:{id:"11111111-1111-1111-1111-111111111111",email_confirmed_at:"2026-10-29T12:00:00Z"}}}),signInWithPassword:async()=>({data:{},error:null}),signOut:async()=>({data:{},error:null})},',
   'from:name=>{if(name!=="research_intelligence_follows")throw Error("Unexpected table "+name);let operation="select",input=null,filters=[];',
   'const q={select:()=>q,eq:(k,v)=>{filters.push([k,v]);return q},order:()=>q,limit:()=>q,insert:v=>{operation="insert";input=v;return q},update:v=>{operation="update";input=v;return q},delete:()=>{operation="delete";return q},',
   'then:resolve=>{const rows=window.__testFollows;if(operation==="insert")rows.push({...input,opted_in_at:"2026-10-29T13:00:00Z"});',
   'if(operation==="update")for(const row of rows.filter(r=>filters.every(([k,v])=>r[k]===v)))Object.assign(row,input);',
   'if(operation==="delete")for(let i=rows.length-1;i>=0;i--)if(filters.every(([k,v])=>rows[i][k]===v))rows.splice(i,1);',
   'resolve({data:operation==="select"?rows.filter(r=>filters.every(([k,v])=>r[k]===v)):null,error:null})}};return q;}})};'
  ].join('\n');
  await page.route('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.118.0/dist/umd/supabase.min.js',
   route=>route.fulfill({contentType:'application/javascript',status:200,body:mock}));
  await page.route('**/rest/v1/flock_agency_watch_events?**',route=>route.fulfill({
   status:200,contentType:'application/json',body:JSON.stringify([
    {event_key:'test_reviewed_event_2026',locality_key:'houston|TX',source_agency_id:'houston city secretary',
     kind:'contract_document',title:'Reviewed published agreement',summary:'Dated city government contract evidence for review',
     source_url:'https://www.houstontx.gov/citysec/agenda/2022/Aug1622.pdf',
     source_date:'2026-10-28',evidence_tier:'original_government',observed_at:'2026-10-28T18:00:00Z'}
   ])
  }));
  const nav=await page.goto(new URL('professional-intelligence.html',base).href,{waitUntil:'domcontentloaded',timeout:30000});
  assert.equal(nav.status(),200);
  await page.waitForFunction(()=>document.querySelector('#evidenceStatus')?.textContent?.includes('validated'),null,{timeout:18000});
  assert.match(await page.locator('#leadStatus').textContent(),/source-attributed leads/);
  assert((await page.locator('#leadCards button').count())>0);
  assert.match(await page.locator('#selectedStatus').textContent(),/Historical research lead|Reviewed public Watch record/);
  assert((await page.locator('#comparisonList article').count())>0);
  assert((await page.locator('#crossAgency li').count())>2);
  assert.match(await page.locator('#draftBody').inputValue(),/does not seek individual license-plate observations/);
  const download=page.waitForEvent('download');await page.locator('#downloadPackage').click();
  const report=await download;
  const html=fs.readFileSync(await report.path(),'utf8');
  assert(html.includes('Verified-source timeline and appendix'));
  assert(html.includes('Unsent editable records request'));
  assert(html.includes('Official roles to contact'));
  assert(html.includes('Evidence boundary'));
  await page.locator('#feedControls').waitFor({state:'visible',timeout:12000});
  await page.locator('#followJurisdiction').selectOption('houston|TX');
  await page.locator('#saveFollow').click();
  await page.waitForFunction(()=>window.__testFollows.length===1,null,{timeout:8000});
  assert.match(await page.locator('#newFeed').textContent(),/No newly published reviewed events/);
  assert.match(await page.locator('#reviewedFeed').textContent(),/Reviewed published agreement/);
  await page.locator('#deleteFollow').click();
  await page.waitForFunction(()=>window.__testFollows.length===0,null,{timeout:8000});
  assert.equal(await page.locator('#followList p').count(),0);
  assert.deepEqual(errors,[]);
  console.log('PROFESSIONAL_INTELLIGENCE_BROWSER_PASS: leads, comparisons, acquisition, print package, private follow, no historical replay, deletion');
 }catch(error){
  console.error('PROFESSIONAL_INTELLIGENCE_BROWSER_FAILED:',error.stack||error.message);
  console.error('SOURCE_STATUS:',await page.locator('#evidenceStatus').textContent().catch(()=>'?'),
   'FOLLOW_STATUS:',await page.locator('#feedStatus').textContent().catch(()=>'?'),
   'ERRORS:',errors.slice(0,8));
  process.exitCode=1;
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
