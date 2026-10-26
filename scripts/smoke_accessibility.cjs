/* Milestone 8 keyboard/screen-size accessibility regression (not a WCAG audit). */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 try{
  for(const width of [390,1280]){
   const page=await browser.newPage({viewport:{width,height:850},reducedMotion:'reduce'});
   for(const path of ['index.html','accountability.html','analytics.html','records.html']){
    const response=await page.goto(new URL(path,base).href,{waitUntil:'domcontentloaded',timeout:45000});
    assert.equal(response.status(),200,path+' not deployed');
    assert.equal(await page.locator('main#main-content').count(),1);
    assert.equal(await page.locator('a.skip-link[href="#main-content"]').count(),1);
    await page.keyboard.press('Tab');
    assert.equal(await page.evaluate(()=>document.activeElement?.getAttribute('href')),
      '#main-content',path+' has no keyboard-accessible skip link');
    if(path==='index.html'){
      assert.equal(await page.locator('#map').getAttribute('tabindex'),'0',
        'Interactive map not keyboard-focusable');
      assert.equal(await page.locator('#map').getAttribute('aria-describedby'),'mapKeyboardHelp');
      assert.ok((await page.locator('#mapKeyboardHelp').textContent()).includes('arrow keys'),
        'Map keyboard controls not explained');
      await page.locator('#map').focus();
      assert.equal(await page.evaluate(()=>document.activeElement?.id),'map',
        'Keyboard navigation cannot focus map');
    }
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
    if(overflow>4) {
      const offenders=await page.evaluate(()=>
        [...document.querySelectorAll('main *, header *')]
          .map(n=>({tag:n.tagName,id:n.id,className:typeof n.className==='string'?n.className:'',
            right:Math.round(n.getBoundingClientRect().right),
            left:Math.round(n.getBoundingClientRect().left),
            width:Math.round(n.getBoundingClientRect().width)}))
          .filter(n=>n.right>innerWidth+4||n.left< -4)
          .sort((a,b)=>b.right-a.right).slice(0,10));
      const probe=await page.evaluate(()=>{
        const report=n=>{const rect=n.getBoundingClientRect();const st=getComputedStyle(n);
          return {tag:n.tagName,id:n.id,cls:typeof n.className==='string'?n.className:'',
            sw:n.scrollWidth,cw:n.clientWidth,ow:n.offsetWidth,rectLeft:Math.round(rect.left),
            rectRight:Math.round(rect.right),overflowX:st.overflowX,
            text:(n.textContent||'').trim().slice(0,95)}};
        return {html:report(document.documentElement),body:report(document.body),
          parents:[...document.querySelectorAll('body *')]
            .filter(n=>n.scrollWidth>n.clientWidth+10||n.getBoundingClientRect().width>innerWidth)
            .sort((a,b)=>(b.scrollWidth-b.clientWidth)-(a.scrollWidth-a.clientWidth))
            .slice(0,16).map(report)};
      });
      const ranges=await page.evaluate(()=>{
        const out=[];const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
        for(let node=walker.nextNode();node;node=walker.nextNode()){
          if(!node.textContent?.trim()||!node.parentElement)continue;
          const style=getComputedStyle(node.parentElement);
          if(style.display==='none')continue;
          const r=document.createRange();r.selectNodeContents(node);
          const box=r.getBoundingClientRect();
          if(box.right>innerWidth+5||box.left< -5){
            out.push({parent:node.parentElement.tagName,id:node.parentElement.id,
              text:node.textContent.trim().slice(0,130),
              left:Math.round(box.left),right:Math.round(box.right),
              width:Math.round(box.width)});
          }
        }
        const br=document.body.getBoundingClientRect();
        return {visibleTextOverflows:out.slice(0,15),
          bodyDirectChildren:[...document.body.childNodes].slice(0,25).map(n=>
            ({type:n.nodeType,node:n.nodeName,txt:n.textContent?.slice(0,50)})),
          bodyBox:{left:br.left,right:br.right,width:br.width}};
      });
      console.error('ACCESSIBILITY TEXTNODE RANGE DIAGNOSTIC',path,width,JSON.stringify(ranges));
      console.error('ACCESSIBILITY OVERFLOW SCROLLWIDTH DIAGNOSTIC',path,width,JSON.stringify(probe));
      console.error('ACCESSIBILITY MOBILE OVERFLOW ELEMENTS',path,width,JSON.stringify(offenders));
    }
    assert.ok(overflow<=4,path+' unexpectedly overflows '+width+'px viewport: '+overflow);
   }
   await page.close();
  }
  console.log('ACCESSIBILITY SHELL PASS: navigation bypass and mobile/desktop width');
 }catch(e){console.error('ACCESSIBILITY SHELL FAIL:',e.message);process.exitCode=1;}
 finally{await browser.close();}
})().catch(e=>{console.error('Accessibility smoke harness failed:',e.message);process.exitCode=1});
