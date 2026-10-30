(async()=>{
'use strict';
const $=id=>document.getElementById(id);
const add=(parent,tag,content)=>{const e=document.createElement(tag);if(content!==undefined)e.textContent=String(content);parent.append(e);return e};
const link=(parent,url,title)=>{
 try{const parsed=new URL(url);if(parsed.protocol!=='https:')return add(parent,'span','Source URL withheld');
 const a=add(parent,'a',title);a.href=parsed.href;a.target='_blank';a.rel='noopener noreferrer';return a;}
 catch{return add(parent,'span','Invalid original URL')}
};
try{
 const r=await fetch('./data/manual-original-evidence-review-2026-10-29.json',
  {cache:'no-store',referrerPolicy:'no-referrer'});
 if(!r.ok)throw Error('Original evidence status HTTP '+r.status);
 const data=await r.json();
 if(data.schema_version!==1||data.discovery_candidates.length!==6||
   data.held_sources.length!==16||data.changed_source_candidates.length!==25)
  throw Error('Incomplete editorial source ledger');
 for(const s of data.discovery_candidates){
  const art=add($('sourceCards'),'article');add(art,'h3',s.title);
  add(art,'p',s.status==='original_pdf_page_visually_verified'?
    'Visually inspected original government PDF, page '+s.page+
    (s.additional_page?' and '+s.additional_page:''):
    'Government index verified, but linked PDF content still held');
  add(art,'p',s.claim);add(art,'small','Evidence limitation: '+s.caveat);
  const l=add(art,'p');link(l,s.url+(s.page?'#page='+s.page:''),'Original government document');
  if(s.parent){const extra=add(art,'p');link(extra,s.parent,'Government index / parent page')}
 }
 for(const h of data.held_sources){
  const row=add($('heldTable'),'tr');
  add(row,'td',h.state+' · '+h.source_id);
  add(row,'td',h.monitor_status);
  const cell=add(row,'td');add(cell,'span',h.disposition);
  if(h.verified_alternative_url){add(cell,'span',' · ');link(cell,h.verified_alternative_url,'Government evidence')}
 }
 for(const c of data.changed_source_candidates){
  const item=add($('changeList'),'li');
  add(item,'strong',c.source_id);
  add(item,'span',' — Before/after original bytes unavailable; held for source-anchored review. No policy change inferred.');
 }
 for(const c of data.comparative_research_findings){
  const box=add($('comparisons'),'article');add(box,'h3','Cross-period reported difference (not source-version approval)');
  add(box,'p',c.claim);add(box,'p',c.caveat);
  link(add(box,'p'),c.before_url,'Earlier government report, page 1');
  link(add(box,'p'),c.after_url,'Later government report, page 1');
 }
 $('reviewStatus').textContent='Originals with visually inspected content: '+data.review_summary.individual_pdf_content_visually_verified+
  '/6; held URLs dispositioned: 16/16; hash differences triaged: 25/25; independently approved document-version changes: 0.';
}catch(e){$('reviewStatus').textContent='Original evidence review held: '+e.message}
})();