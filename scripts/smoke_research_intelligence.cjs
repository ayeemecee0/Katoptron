'use strict';
const {chromium}=require('playwright');
async function run(){
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:390,height:844}});
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 const problems=[];page.on('pageerror',e=>problems.push(e.message));
 async function go(route){
  await page.goto(new URL(route,base).href,{waitUntil:'domcontentloaded',timeout:30000});
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+3);
  if(overflow)throw Error('New research view overflows mobile viewport: '+route);
 }
 try{
  await go('agency-intelligence-hub.html');
  await page.locator('#cards .card').first().waitFor({timeout:15000});
  const count=await page.locator('#cards .card').count();
  if(count<35)throw Error('New nationwide source publishers missing: '+count);
  await page.selectOption('#state','KY');
  if(await page.locator('#cards .card').count()!==1)throw Error('Kentucky issuer not indexed');
  await page.locator('#cards .card button').click();
  await page.locator('#details:not([hidden])').waitFor();
  if(!/Frankfort/.test(await page.locator('#detailTitle').innerText()))throw Error('Exact agency not selected');
  if(!/source-stated|unknown/i.test(await page.locator('#quick').innerText()))throw Error('Source amount boundary not stated');
  if(await page.locator('#timeline a').count()<1)throw Error('Original government citation missing');
  if(!/research-workspace.html/.test(await page.locator('#actions a').last().getAttribute('href')))
    throw Error('Save source-backed case link missing');
  await go('agency-government-brief.html?id=frankfort-ky-flock-nonrenewal-commission-vote-2026');
  await page.locator('#report:not([hidden])').waitFor({timeout:18000});
  if(!/Frankfort/.test(await page.locator('#heading').innerText()))throw Error('New public source dossier failed');
  await page.route('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.118.0/dist/umd/supabase.min.js',
   async route=>route.fulfill({status:200,contentType:'application/javascript',
    body:'window.supabase={createClient:()=>({auth:{getUser:async()=>({data:{user:null},error:{name:"AuthSessionMissingError",message:"No session"}})}})};'}));
  await go('research-workspace.html');
  await page.locator('#signin:not([hidden])').waitFor({timeout:10000});
  if(!(await page.locator('#workspaceApp').isHidden()))throw Error('Private research workspace exposed before authentication');
  if(!/Sign in/.test(await page.locator('#status').innerText()))throw Error('Unconfirmed workspace auth gate');
  if(problems.length)throw Error('Browser script failures: '+problems.slice(0,3).join(' | '));
  console.log('RESEARCH_INTELLIGENCE_MOBILE_PASS',
   JSON.stringify({governmentIssuers:count,kentuckyExactIssuer:true,originalCitation:true,privateLoginGate:true,errors:0}));
 }finally{await browser.close()}
}
run().catch(e=>{console.error(e);process.exitCode=1});
