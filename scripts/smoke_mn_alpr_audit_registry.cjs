const {chromium}=require('playwright');
const assert=require('node:assert/strict');

(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 const page=await browser.newPage({viewport:{width:390,height:844}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const rows=[
  {source_url:'https://www.lrl.mn.gov/docs/2026/mandated/261013.pdf',registry_url:'https://www.lrl.mn.gov/mndocs/mandates_detail?orderid=8735',
   report_id:'26-1013.pdf',report_title:'Shakopee Police Department 2026 ALPR Audit (Flock System)',listed_publishers:'City of Shakopee',
   publication_date:'2026-06-15',coverage_period:'2024 to 2026',received_date:'2026-06-17',
   title_scope:'flock_named_in_title',evidence_tier:'state_legislative_registry_index_metadata_only'},
  {source_url:'https://www.lrl.mn.gov/docs/2025/mandated/251753.pdf',registry_url:'https://www.lrl.mn.gov/mndocs/mandates_detail?orderid=8735',
   report_id:'25-1753.pdf',report_title:'Oakdale Police 2025 ALPR Audit (Motorola)',listed_publishers:'City of Oakdale',
   publication_date:'2025-11-10',coverage_period:'',received_date:'2025-11-10',
   title_scope:'other_vendor_named_in_title',evidence_tier:'state_legislative_registry_index_metadata_only'},
  {source_url:'https://www.lrl.mn.gov/docs/2026/mandated/261569.pdf',registry_url:'https://www.lrl.mn.gov/mndocs/mandates_detail?orderid=8735',
   report_id:'26-1569.pdf',report_title:'Otter Tail County Sheriff Independent ALPR Audit',listed_publishers:'Otter Tail County',
   publication_date:'2026-10-04',coverage_period:'November 2024 to July 2026',received_date:'2026-10-07',
   title_scope:'unspecified_alpr_title',evidence_tier:'state_legislative_registry_index_metadata_only'}
 ];
 try{
  await page.route('**/rest/v1/flock_public_mn_alpr_audit_registry?**',async route=>{
   await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(rows)});
  });
  const url=new URL('mn-alpr-audits.html?q=Shakopee',base).href;
  const r=await page.goto(url,{waitUntil:'domcontentloaded',timeout:25000});
  assert.equal(r.status(),200);
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent?.includes('official archive report'),
   null,{timeout:12000});
  assert.match(await page.locator('#status').textContent(),/^1 official archive/);
  assert.equal(await page.locator('#reports article').count(),1);
  assert.match(await page.locator('#reports').textContent(),/Shakopee/);
  assert.match(await page.locator('#reports').textContent(),/Flock mentioned in title/);
  const source=await page.locator('#reports article a').first().getAttribute('href');
  assert.equal(source,'https://www.lrl.mn.gov/docs/2026/mandated/261013.pdf');
  await page.locator('#query').fill('');
  await page.locator('#scope').selectOption('other_vendor_named_in_title');
  assert.equal(await page.locator('#reports article').count(),1);
  assert.match(await page.locator('#reports').textContent(),/Oakdale/);
  assert.doesNotMatch(await page.locator('#reports').textContent(),/Flock mentioned in title/);
  await page.locator('#scope').selectOption('all');
  assert.equal(await page.locator('#reports article').count(),3);
  assert.match(await page.locator('main').textContent(),/not a verified current manufacturer/);
  const fits=await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+2);
  assert.ok(fits,'390px mobile viewport must not overflow');
  // A second pass adds official, not-yet-reviewed titles. The queue must
  // reconcile exact agency identity without publishing camera or Flock facts.
  rows.push({
   source_url:'https://www.lrl.mn.gov/docs/2022/mandated/220708.pdf',
   registry_url:'https://www.lrl.mn.gov/mndocs/mandates_detail?orderid=8735',
   report_id:'22-0708.pdf',
   report_title:'Independent Audit of Shakopee Police Department ALPR System',
   listed_publishers:'Minnesota state archive',
   publication_date:'2022-05-08',coverage_period:'2020–2022',received_date:'2022-05-09',
   title_scope:'unspecified_alpr_title',evidence_tier:'state_legislative_registry_index_metadata_only'
  });
  rows.push({
   source_url:'https://www.lrl.mn.gov/docs/2026/mandated/261268.pdf',
   registry_url:'https://www.lrl.mn.gov/mndocs/mandates_detail?orderid=8735',
   report_id:'26-1268.pdf',
   report_title:'Wyoming Police Department 2026 ALPR Audit (Flock System)',
   listed_publishers:'Minnesota state archive',
   publication_date:'2026-08-30',coverage_period:'2025–2026',received_date:'2026-09-02',
   title_scope:'flock_named_in_title',evidence_tier:'state_legislative_registry_index_metadata_only'
  });
  rows.push({
   source_url:'https://www.lrl.mn.gov/docs/2027/mandated/270188.pdf',
   registry_url:'https://www.lrl.mn.gov/mndocs/mandates_detail?orderid=8735',
   report_id:'27-0188.pdf',
   report_title:'Woodbury Public Safety Department Automated License Plate Reader Audit: Executive Summary',
   listed_publishers:'Minnesota state archive',
   publication_date:'2027-01-12',coverage_period:'2019',received_date:'2025-10-30',
   title_scope:'unspecified_alpr_title',evidence_tier:'state_legislative_registry_index_metadata_only'
  });
  await page.reload({waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('#queueStatus')?.textContent?.includes('queued original state audit'),
   null,{timeout:15000});
  assert.match(await page.locator('#queueStatus').textContent(),/^1 queued original state audit/);
  const queue=page.locator('#queueCards article');
  assert.equal(await queue.count(),1);
  assert.match(await queue.first().textContent(),/Woodbury/);
  assert.match(await queue.first().textContent(),/P1/);
  assert.match(await queue.first().textContent(),/Manufacturer not identified in title/);
  assert.ok(!(await page.locator('#queueCards').textContent()).includes('verified current'));
  for(const alreadyReviewed of ['Wyoming Police','West Saint Paul','Shakopee']){
   assert.ok(!(await page.locator('#queueCards').textContent()).includes(alreadyReviewed),
    'Reviewed originals must not remain falsely in the review queue');
  }
  assert.ok(await queue.first().locator('a[href*="agency-audit.html?place=woodbury"]').count());
  assert.equal(await page.locator('#reports article').count(),2);
  assert.deepEqual(errors,[]);
  console.log('OFFICIAL MINNESOTA AUDIT LIBRARY BROWSER PASS: metadata tiers, strict source links, filtering, deep link, mobile');
 }catch(e){console.error('MINNESOTA AUDIT BROWSER FAILED:',e.stack||e,errors);process.exitCode=1;}
 finally{await browser.close()}
})().catch(e=>{console.error(e.stack||e);process.exitCode=1;});
