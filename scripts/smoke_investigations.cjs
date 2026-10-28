'use strict';
const {chromium}=require('playwright');
async function main(){
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 const page=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',err=>errors.push(err.message));
 async function go(route,waitFor){
  await page.goto(new URL(route,base).href,{waitUntil:'domcontentloaded',timeout:40000});
  try{await page.locator(waitFor).waitFor({state:'visible',timeout:18000});}
  catch(error){
   const details=await page.evaluate(()=>({status:document.querySelector('#status')?.textContent,
    body:document.body.textContent.slice(-500)}));
   throw Error(route+': '+error.message+'\nDIAGNOSTIC '+JSON.stringify(details)+
    '\nPAGE ERRORS '+JSON.stringify(errors.slice(-6)));
  }
  const horizontal=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+2);
  if(horizontal)throw Error('Mobile horizontal overflow: '+route);
 }
 try{
  await go('agency-investigation.html?original=green-bay-police-wi&compare=moline-police-il',
   '#report:not([hidden])');
  const investigation=await page.locator('#findings article').count();
  if(investigation<6)throw Error('Lost verified source-page findings '+investigation);
  if(await page.locator('#comparisonPanel').isHidden())throw Error('Agency report cross-comparison missing');
  if(await page.locator('#print').isDisabled())throw Error('Printable report not enabled');
  if(await page.locator('#timeline article').count()!==1)throw Error('Draft proposal status missing');
  if(!/Source fingerprints|original/i.test(await page.locator('#meta').innerText()))
   throw Error('Investigative export metadata missing');
  await go('surveillance-changes.html','#events article');
  if(await page.locator('#events article').count()!==4)
   throw Error('Expected four source-status change/proposal records');
  await page.selectOption('#kind','proposal');
  if(await page.locator('#events article').count()!==1)
   throw Error('Draft wrongly shown as signed change');
  await page.selectOption('#kind','substantive');
  if(await page.locator('#events article').count()!==3)
   throw Error('Signed changes/proposals boundary failed');
  await page.selectOption('#state','AZ');
  if(await page.locator('#events article').count()!==1)throw Error('AZ filter failed');
  await go('agency-compare.html?a=moline-police-il&b=oklahoma-city-ok&topic=contracts',
   '#intelligenceMatrix:not([hidden])');
  if(await page.locator('#intelligenceColumns .agency').count()!==2)
   throw Error('Cross-agency source intelligence missing');
  await go('agency-xray.html?original=moline-police-il',
   '#investigationSummary:not([hidden])');
  if(!/page-cited findings/i.test(await page.locator('#intelligenceStatus').innerText()))
   throw Error('One-page agency summary unavailable');
  if(await page.locator('#intelligenceTopics .card').count()<5)
   throw Error('Agency summary topics not integrated');
  if(!/original=moline-police-il/.test(await page.locator('#investigationExport').getAttribute('href')))
   throw Error('One-click source-cited report not wired');
  if(errors.length)throw Error('Client JS errors: '+errors.slice(0,3).join(' | '));
  console.log('M12_INTEGRATED_INTELLIGENCE_MOBILE_PASS',
   JSON.stringify({originalFindings:investigation,signedChanges:3,proposals:1,
    crossAgencyColumns:2,agencyTopics:5,errors:0}));
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1});
