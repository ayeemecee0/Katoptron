/* Read-only Milestone 7 browser acceptance: no tracking or write actions. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1120,height:900}});
 try{
  const base=process.env.KATOPTRON_SMOKE_BASE||'https://ayeemecee0.github.io/Katoptron/';
  const response=await page.goto(new URL('analytics.html',base).href,{waitUntil:'domcontentloaded',timeout:45000});
  assert.equal(response.status(),200,'Evidence analytics missing from public site');
  await page.waitForFunction(()=>/Loaded fully reconciled published evidence|analytics unavailable/.test(
    document.querySelector('#status')?.textContent||''),{timeout:45000});
  assert.match(await page.locator('#status').textContent(),/Loaded fully reconciled published evidence/);
  assert.ok(Number((await page.locator('#exact').textContent()).replaceAll(',',''))>=1,
    'Published exact camera inventory unavailable');
  const number=async id=>Number((await page.locator('#'+id).textContent()).replaceAll(',',''));
  assert.equal(await number('exact'),await number('flock')+await number('generic')+await number('unknown'),
    'Every original government location must have exactly one source manufacturer category');
  assert.ok(await number('flock')>=1,'Verified positive Flock government source tier unavailable');
  assert.ok(await number('provisional')>=0&&await number('corroborated')>=0);
  const states=await page.locator('#stateRows tr').count();
  assert.ok(states>=1,'State source breakdown unavailable');
  assert.equal(await page.locator('#stateRows tr:first-child td').count(),8,
    'Government manufacturer-source tiers must remain visible per state');
  assert.ok((await page.locator('#timeChart [role="listitem"]').count())>=1,
    'Source-dated chronological evidence unavailable');
  await page.locator('#sort').selectOption('name');
  await page.locator('#category').selectOption('government_program');
  assert.equal(await page.locator('#download').isEnabled(),true);
  const downloadPromise=page.waitForEvent('download');
  await page.locator('#download').click();
  const download=await downloadPromise;
  assert.equal(download.suggestedFilename(),'katoptron-source-evidence-by-state.csv');
  // A deliberately malformed but apparently successful source response is
  // never a signal that unknown evidence counts are zero.
  await page.route('**/rest/v1/flock_analytics_overview?**',route=>route.fulfill({
    status:200,contentType:'application/json',
    headers:{'access-control-allow-origin':'*','access-control-expose-headers':'content-range'},
    body:JSON.stringify([{exact_government_points:999}])
  }));
  await page.reload({waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>/analytics unavailable or incomplete/.test(
    document.querySelector('#status')?.textContent||''),null,{timeout:30000});
  assert.equal(await page.locator('#download').isDisabled(),true,
    'Incomplete national source count must disable statistics export');
  console.log('ANALYTICS PASS: exact Flock/generic manufacturer-source reconciliation, dated records, CSV and fail-closed incomplete source');
 }catch(error){console.error('ANALYTICS FAIL:',error.message);process.exitCode=1;}
 finally{await browser.close();}
})().catch(error=>{console.error('Analytics smoke failed:',error.message);process.exitCode=1});
