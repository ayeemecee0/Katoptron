/* M8 browser-only adversarial accessibility checks.
   Tests emulate 320 CSS px (400% zoom proxy on a 1280px display),
   Windows forced-colors, text spacing and control hit targets.
   This is NOT a human screen-reader or real-device certification. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
const files=['index.html','records.html','accountability.html','analytics.html',
 'submit.html','community-review.html','privacy.html','methodology.html',
 'portals.html','community-map.html','nearby.html'];
const browserErrors=[];
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const file of files){
   const context=await browser.newContext({viewport:{width:320,height:720},
      forcedColors:'active',reducedMotion:'reduce'});
   const page=await context.newPage();
   page.on('pageerror',e=>browserErrors.push({file,error:e.message}));
   const response=await page.goto(new URL(file,base).href,
      {waitUntil:'domcontentloaded',timeout:40000});
   assert.equal(response?.status(),200,file+' missing');
   await page.waitForTimeout(150);
   let report=await page.evaluate(()=>{
    const $=(sel)=>document.querySelector(sel);
    const main=$('main#main-content');
    const skip=$('a.skip-link[href="#main-content"]');
    const width=window.innerWidth;
    const doc=document.documentElement.scrollWidth;
    const controls=[...document.querySelectorAll('button,select,summary,.masthead nav a')].
      filter(el=>!el.disabled&&el.getClientRects().length&&
        getComputedStyle(el).visibility!=='hidden');
    const small=controls.map(el=>{
      const rect=el.getBoundingClientRect();
      return {tag:el.tagName,id:el.id,text:(el.textContent||'').trim().slice(0,32),
        width:Math.round(rect.width),height:Math.round(rect.height)};
    }).filter(x=>x.height<24||x.width<24);
    const focus=getComputedStyle(skip,':focus-visible');
    return {hasMain:!!main,hasSkip:!!skip,width,doc,small,
      reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches,
      forcedColors:matchMedia('(forced-colors: active)').matches};
   });
   assert.ok(report.hasMain&&report.hasSkip,file+' missing skip/main');
   assert.ok(report.reducedMotion&&report.forcedColors,file+' preference emulation failed');
   assert.ok(report.doc<=report.width+4,file+' 320 CSS pixel viewport overflows '+JSON.stringify(report));
   assert.deepEqual(report.small,[],file+' undersized action targets: '+JSON.stringify(report.small));
   await page.keyboard.press('Tab');
   assert.equal(await page.evaluate(()=>document.activeElement?.getAttribute('href')),
     '#main-content',file+' keyboard skip link not first');
   const skipFocus=await page.evaluate(()=>{
     const link=document.activeElement,style=getComputedStyle(link);
     const rect=link.getBoundingClientRect();
     return {height:rect.height,top:rect.top,left:rect.left,
       outlineStyle:style.outlineStyle,outlineWidth:style.outlineWidth,
       transform:style.transform,scrollY:scrollY,
       matchedFocus:link.matches(':focus'),matchedVisible:link.matches(':focus-visible'),
       sheets:[...document.styleSheets].map(s=>s.href||'(inline)').filter(Boolean),
       cssText:[...document.querySelectorAll('link[rel=stylesheet]')].map(x=>({
         href:x.getAttribute('href'),loaded:!!x.sheet}))};
   });
   assert.ok(skipFocus.height>=24&&skipFocus.top>=-1&&skipFocus.left>=-1&&
     skipFocus.outlineStyle!=='none'&&parseFloat(skipFocus.outlineWidth)>=2,
     file+' focused skip target invisible in system high contrast: '+JSON.stringify(skipFocus));
   // WCAG 1.4.12 letter + word + paragraph spacing stress, with no document
   // horizontal overflow. These are CSS overrides, not speech synthesis.
   await page.addStyleTag({content:`
     *:not(svg):not(path){letter-spacing:.12em!important;
       word-spacing:.16em!important}
     p,li,label{line-height:1.5!important}
     p{margin-bottom:2em!important}
   `});
   const after=await page.evaluate(()=>({
     w:document.documentElement.scrollWidth,viewport:innerWidth
   }));
   assert.ok(after.w<=after.viewport+4,
     file+' spacing override causes horizontal document clipping '+JSON.stringify(after));
   console.log('M8 ADVERSARIAL ACCESSIBILITY PASS',file,
     '320px forced-colors targets/reflow, visible skip focus and text spacing');
   await context.close();
  }
  assert.deepEqual(browserErrors,[],'Uncaught browser accessibility errors');
  console.log('M8 ADVERSARIAL BROWSER PASS: 11 anonymous pages; no manual-AT claim');
 }catch(error){
  console.error('M8 ADVERSARIAL BROWSER FAIL',error.stack||error);
  process.exitCode=1;
 }finally{await browser.close();}
})().catch(e=>{console.error('M8 browser harness error',e.stack||e);process.exitCode=1});
