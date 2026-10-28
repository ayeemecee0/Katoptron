'use strict';
const { chromium }=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:390,height:844},isMobile:true,deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
  await page.goto(new URL('policy-evidence-issues.html',base).href,{waitUntil:'networkidle'});
  await page.getByText('5 source questions / interpretation cautions displayed').waitFor();
  const count=await page.locator('#cards article').count();
  if(count!==5)throw Error('Expected five evidence question cards, got '+count);
  await page.selectOption('#stateFilter','WA');
  if(await page.locator('#cards article').count()!==2)throw Error('WA filter regression');
  await page.selectOption('#kindFilter','context');
  if(await page.locator('#cards article').count()!==0)throw Error('Context/state filter mismatch');
  await page.selectOption('#stateFilter','ALL');
  if(await page.locator('#cards article').count()!==1)throw Error('Context caution is missing');
  if(errors.length)throw Error('Page error: '+errors.join('; '));
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+2);
  if(overflow)throw Error('Mobile viewport overflow');
  console.log('POLICY_EVIDENCE_ISSUES_BROWSER_PASS',JSON.stringify({all:count,wa:2,cautions:1,errors:0}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
