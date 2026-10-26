/* Milestone 6: public browser smoke, no authentication and no source promotion.
 * Checks the actual public read contract and labels, not invented seed data. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1240,height:850}});
 const base=process.env.KATOPTRON_SMOKE_BASE||'https://ayeemecee0.github.io/Katoptron/';
 try{
  const response=await page.goto(new URL('accountability.html',base).href,
   {waitUntil:'domcontentloaded',timeout:45000});
  assert.equal(response.status(),200,'Accountability page not published');
  await page.waitForFunction(()=>{
   const x=document.querySelector('#status')?.textContent||'';
   return /matching published records/.test(x)||/unavailable/.test(x);
  },{timeout:45000});
  const status=await page.locator('#status').textContent();
  assert.match(status,/matching published records/,'Public accountability API inaccessible: '+status);
  assert.ok((await page.locator('#results article.entry').count())>=1,'No evidence cards rendered');
  assert.equal(await page.locator('#export').isEnabled(),true);
  await page.selectOption('#type','recorded_legislative_decision');
  await page.locator('#search').fill('Bellevue');
  assert.ok((await page.locator('#results article.entry').count())>=1,
    'Bellevue original government signed-off council outcome not publicly indexed');
  assert.ok((await page.locator('#results').textContent()).includes('March 24, 2025')||
    (await page.locator('#results').textContent()).includes('2025-03-24'),
    'Bellevue official decision date not shown');
  await page.locator('#search').fill('');
    await page.selectOption('#type','agenda_mention');
  const statusAfter=await page.locator('#status').textContent();
  assert.match(statusAfter,/matching published records/);
  await page.locator('#peopleTab').click();
  assert.equal(await page.locator('#peoplePanel').isVisible(),true);
  assert.ok((await page.locator('#peopleResults article.entry').count())>=1,'No dated primary-source roles');
  const originalVotes=page.locator('#positionResults article.entry');
  assert.ok((await originalVotes.count())>=5,
    'Original named government votes need at least five source-backed Bellevue positions');
  const namedText=await page.locator('#positionResults').textContent();
  assert.ok(namedText.includes('Tom Bergin')&&namedText.includes('Suzanne Wrede')&&
    namedText.includes('Tammy E. Davis'), 'Flock original voted names missing');
  assert.ok(namedText.includes('Original named government record'), 'Each vote needs direct source link');
  await page.locator('#recordsTab').click();
  assert.equal(await page.locator('#recordsPanel').isVisible(),true);
  console.log('MILESTONE 6 PUBLIC PASS: feed, filtering, original citations, professional role classifications');
 }catch(error){
  console.error('MILESTONE 6 PUBLIC FAIL:',error.message);
  process.exitCode=1;
 }finally{await browser.close();}
})().catch(error=>{console.error('Milestone 6 smoke harness error:',error.message);process.exitCode=1});
