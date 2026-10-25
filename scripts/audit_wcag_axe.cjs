/* Automated WCAG 2.2 A/AA screening. Not manual AT certification.
 * Local test server only, anonymous pages only: never exercise real login.
 * Logs rules/impact/counts, never URLs, user input, or private content.
 */
const {chromium}=require('playwright');
const AxeBuilder=require('@axe-core/playwright').default;
const assert=require('node:assert/strict');
const pages=['index.html','records.html','accountability.html','analytics.html',
  'submit.html','community-review.html','privacy.html','methodology.html','portals.html'];
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 let severe=0,moderate=0;
 const host='http://127.0.0.1:8765/';
 try{
  for(const width of [390,1280]){
   const context=await browser.newContext({viewport:{width,height:850},reducedMotion:'reduce'});
   const page=await context.newPage();
   for(const file of pages){
    const r=await page.goto(host+file,{waitUntil:'domcontentloaded',timeout:30000});
    assert.equal(r?.status(),200,'Missing audited page '+file);
    await page.waitForTimeout(150);
    const audit=await new AxeBuilder({page})
      .withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa'])
      .analyze();
    const problems=audit.violations.map(x=>({
      id:x.id,impact:x.impact,count:x.nodes.length,
      targets:x.nodes.slice(0,5).map(node=>node.target)
    }));
    for(const item of problems){
      if(item.impact==='critical'||item.impact==='serious')severe+=item.count;
      else moderate+=item.count;
    }
    console.log('WCAG SCAN',file,width,'violations',
      JSON.stringify(problems));
   }
   await context.close();
  }
  console.log('WCAG AUTOMATED SUMMARY: serious_or_critical='+severe+
    ' moderate_or_minor='+moderate);
  assert.equal(severe,0,'Serious or critical WCAG rule violations remain');
  assert.equal(moderate,0,'Moderate or minor WCAG rule violations remain');
  console.log('WCAG AUTOMATED PASS: evaluated rules on anonymous pages, two viewports.');
  console.log('Manual NVDA/VoiceOver, touch, zoom and provider account checks still required.');
 }catch(error){
  console.error('WCAG AUTOMATED AUDIT FAILED:',error.message);
  process.exitCode=1;
 }finally{await browser.close();}
})().catch(e=>{console.error('Accessibility test harness error:',e.name);process.exitCode=1});
