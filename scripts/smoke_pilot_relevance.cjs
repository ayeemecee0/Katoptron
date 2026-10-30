'use strict';
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:1100,height:850},acceptDownloads:true});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 try{
  const u=new URL('pilot-research.html?focus=public_spending&agency=houston%7CTX',base);
  const result=await page.goto(u.href,{waitUntil:'domcontentloaded',timeout:25000});
  assert.equal(result.status(),200);
  await page.waitForFunction(()=>document.querySelector('#recommendationStatus')?.textContent?.includes('Showing'),null,{timeout:15000});
  assert.equal(await page.locator('#researchFocus').inputValue(),'public_spending');
  assert.equal(await page.locator('#researchAgency').inputValue(),'houston|TX');
  assert.equal(await page.locator('#recommendations article').count(),1);
  assert.equal(await page.locator('#sourceItems article').count(),2);
  assert.match(await page.locator('#dossierStatus').textContent(),/2 individually reviewed/);
  const links=await page.locator('#sourceItems a').evaluateAll(nodes=>nodes.map(x=>x.href));
  assert(links.some(x=>x.includes('Aug1622.pdf')));
  assert(links.some(x=>x.includes('Sep2722.pdf')));
  assert.match(await page.locator('#openQuestions').textContent(),/amendment|invoices|payments/i);
  const dl=page.waitForEvent('download');await page.locator('#downloadPacket').click();
  const f=await dl,c=fs.readFileSync(await f.path(),'utf8');
  assert.match(c,/2022-09-28/);assert.match(c,/2022-08-17/);
  assert(c.includes('Ordinance 2022-0727'));assert(c.includes('Ordinance 2022-0629'));
  assert(c.includes('Source basis'));assert(c.includes('Neither the selection score'));
  assert(!c.includes('actual paid expenditure verified'));
  const query=new URL(await page.locator('#inspectAgency').getAttribute('href'));
  assert.equal(query.searchParams.get('agency'),'houston|TX');
  await page.locator('#researchAgency').selectOption('new hanover county|NC');
  await page.locator('#refreshLeads').click();
  assert.equal(await page.locator('#sourceItems article').count(),1);
  assert.match(await page.locator('#dossierStatus').textContent(),/Only 1 original-government record/);
  assert.match(await page.locator('#sourceItems').textContent(),/vendor|Flock|procurement/i);
  await page.locator('#researchAgency').selectOption('');
  await page.locator('#researchQuestion').fill('contract renewal');
  await page.locator('#refreshLeads').click();
  assert((await page.locator('#recommendations article').count())>=3);
  assert.deepEqual(errors,[]);
  console.log('PILOT_RELEVANCE_BROWSER_PASS: verified Houston two-doc packet, dated sources and claims, single-record NC honesty, research filters and no-account access');
 }catch(e){
  console.error('PILOT_RELEVANCE_BROWSER_FAILED:',e.stack||e.message);
  console.error('STATUS:',await page.locator('#recommendationStatus').textContent().catch(()=>'?'),'ERRORS:',errors);
  process.exitCode=1;
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
