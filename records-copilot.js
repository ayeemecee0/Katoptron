/* Public records research copilot. Pure, local-only draft assembly.
 * No external API calls, statutory deadline estimation or autonomous sends.
 * Response dispositions are chosen by researchers, never inferred from uploaded files.
 */
(function(root,factory){
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronRecordsCopilot=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const RECORD_TYPES=Object.freeze({
  contract:{label:'Executed contracts and expenditure',records:[
   'The executed agreement and all signed amendments or renewals related to the identified program.',
   'The procurement approval, award or sole-source justification, including signed authorization.',
   'Existing purchase orders, invoices and aggregate payment or encumbrance records for the specified period.'
  ],caveat:'Budget approval does not prove an executed contract, disbursement or active cameras.'},
  policy:{label:'Policy adoption and versions',records:[
   'The dated, approved policy, its predecessor and version or adoption history for this program.',
   'Existing decision memos, staff reports and adoption or approval minutes establishing the effective date.',
   'Aggregate documented training and policy-review completion records for the specified period.'
  ],caveat:'Publication and revision dates do not independently establish when a rule took effect.'},
  oversight:{label:'Audits and oversight',records:[
   'Existing aggregate internal or independent audit reports and any corrective-action summaries for this program.',
   'The adopted audit methodology, schedule and written supervisory oversight requirements.',
   'Dated aggregate completion and remediation records, excluding personal plate or individual investigative data.'
  ],caveat:'A published audit policy does not prove each audit happened.'},
  sharing:{label:'Access, retention and sharing',records:[
   'Executed agency-to-agency sharing agreements, approved access lists and dated approval or revocation decisions.',
   'Written retention settings, deletion procedures and aggregate compliance/audit results for the period.',
   'Existing aggregate access-permission change records, not individual searches or plate sightings.'
  ],caveat:'Authorization to share is not evidence that a specific query or disclosure occurred.'},
  termination:{label:'Termination and decommissioning',records:[
   'Council minutes or written decision authorizing discontinuation and any signed notice of contract termination.',
   'Vendor acknowledgment, final service end date and relevant settlement or termination payment documents.',
   'Existing aggregate records confirming deactivation, removal or data-retention closure, where maintained.'
  ],caveat:'An announced intent to terminate is not proof of contract closure or device removal.'}
 });
 const OUTCOMES=Object.freeze({
  acknowledged:{label:'Acknowledgment / tracking number',next:'Please confirm the assigned tracking or reference number, the responsible records custodian and an estimated date for the next status update. No statutory deadline is presumed.',next_action:'Record acknowledgment date and reference number, then set your own follow-up date.'},
  delayed:{label:'Still being processed / delay',next:'Please provide the current processing status, what scope is still under review and an estimated date for completion or the next update.',next_action:'Save the actual agency response and manually set a follow-up date; do not call it a legal violation.'},
  partial:{label:'Partial document production',next:'Please identify which requested categories were produced and which remain pending or withheld. For withheld portions, please identify the stated basis and provide any reasonably segregable public portions.',next_action:'Compare supplied originals to each requested document category and identify gaps without assuming omission.'},
  fees:{label:'Fee estimate / deposit requested',next:'Please provide an itemized estimate of search, duplication and review charges, if applicable, and describe available narrowing options or fee-reduction procedures. Please do not incur fees above my separately confirmed limit without authorization.',next_action:'Check the agency-specific fee rules and narrow scope before accepting any estimate.'},
  denial:{label:'Withheld records / exemption claimed',next:'Please identify the specific records or categories withheld, the stated legal provision and a description of reasonably segregable public portions. If an administrative review or appeal process is available, please provide its official instructions.',next_action:'Verify the governing local law and appeal procedure independently; no deadline or right is inferred.'},
  no_records:{label:'No responsive records reported',next:'Please clarify the offices, repositories and date range searched, and whether another custodian may hold responsive records. If appropriate, please refer the request to the correct agency or identify that office.',next_action:'Treat the response as a custodian search result, not proof no document exists anywhere.'},
  referral:{label:'Referred to another custodian',next:'Please identify the receiving records custodian, the transfer or referral date and any tracking identifier. Please confirm whether I should submit the same request directly to that office.',next_action:'Check where responsibility transferred before submitting a duplicate request.'},
  produced:{label:'Records received',next:'Thank you for the records supplied. Please confirm whether this production is complete for the requested categories and whether any responsive portions remain pending or withheld.',next_action:'Inventory documents, confirm versions, hash authentic original files and distinguish receipt from verification.'},
  clarification:{label:'Scope clarification requested',next:'Please identify which terms, date ranges or records categories require clarification. I can narrow the request to existing responsive documents without seeking new analysis or sensitive individual ALPR data.',next_action:'Narrow to named documents, dates and custodians; preserve the original request.'}
 });
 function line(raw,max=200){
  return String(raw??'').replace(/[\x00-\x1f\x7f]+/g,' ').replace(/\s+/g,' ').trim().slice(0,max);
 }
 function safeUrl(raw){
  if(!raw)return null;
  try{const u=new URL(String(raw));
   return u.protocol==='https:'&&!u.username&&!u.password&&!u.port&&!u.hash&&u.hostname.length>=5?u.href:null;
  }catch{return null;}
 }
 function isoDate(value){
  if(!value)return '';
  if(typeof value!=='string'||!/^\d{4}-\d\d-\d\d$/.test(value)||Number.isNaN(Date.parse(value+'T00:00:00Z'))||
      new Date(value+'T00:00:00Z').toISOString().slice(0,10)!==value)
   throw Error('Use a valid YYYY-MM-DD date');
  return value;
 }
 function cost(value){
  if(value==null||value==='')return '';
  if(!/^\d+(?:\.\d{1,2})?$/.test(String(value)))throw Error('Use a nonnegative fee cap in dollars');
  const n=Number(value);if(!Number.isFinite(n)||n>10000)throw Error('Fee cap must be at most $10,000');
  return n.toFixed(2);
 }
 function draft(options={}){
  const topic=options.topic||'contract',spec=RECORD_TYPES[topic];
  if(!spec)throw Error('Choose a documented records category');
  const agency=line(options.agency,150);
  if(agency.length<3)throw Error('Specify the government agency');
  const source=options.source_url?safeUrl(options.source_url):null;
  if(options.source_url&&!source)throw Error('Source link must be an ordinary HTTPS page without embedded credentials or fragments');
  const start=isoDate(options.start_date),end=isoDate(options.end_date);
  if(start&&end&&start>end)throw Error('Start date cannot be after end date');
  const limit=cost(options.fee_cap);
  const custodian=line(options.custodian,200)||'Public Records Officer (government custodian to confirm)';
  const title=line(options.subject,120)||spec.label;
  const scope=start&&end?'From '+start+' through '+end:
   start?'From '+start+' onward (end date not supplied)':
   end?'Records dated on or before '+end+' (start date not supplied)':
   'Date range not yet specified; narrow before submitting';
  const records=spec.records.slice();
  const body=[
   'UNSENT DRAFT — verify official custodian, time window, relevant laws and any fees.',
   'To: '+custodian,'Re: '+title+' — '+agency,'',
   'I request electronic copies of existing, publicly releasable government records, IF HELD, relating to the identified program or decision.',
   'Requested date range: '+scope+'.',
   source?'Original public source for identification: '+source:'Original public source: [insert checked publisher document or official agenda URL].',
   '', 'Please search for the following existing records:',
   ...records.map((r,i)=>(i+1)+'. '+r),
   '', 'Electronic format preferred: '+(['pdf','native','either'].includes(options.format)?{
    pdf:'searchable PDFs where maintained',native:'existing native electronic files where practical',either:'PDFs or existing native formats where practical'}[options.format]:'existing electronic files where practical')+'.',
   limit!==''?'Please notify me and obtain my approval before incurring fees exceeding $'+limit+'.':
    'Please advise me of any applicable fees before incurring them.',
   'Please provide reasonably segregable public portions of responsive records and identify any asserted withholding basis.',
   'I am not requesting individual license-plate observations, location histories, personal case records, hotlists, credentials, or confidential search logs.',
   'If this office does not maintain the responsive records, please identify the appropriate records custodian if known.',
   'This request does not ask the agency to create records or perform new analyses. Please advise of any practical ways to narrow an unduly broad request.',
   '', 'Thank you.'
  ].join('\n');
  return Object.freeze({subject:(title+' — public records request').slice(0,200),custodian,body,records,
   check_before_sending:[
    'Independently verify the receiving agency and its official request submission channel.',
    'Confirm the requested records are reasonably identifiable and dates are sufficiently narrow.',
    'Review source document identity; URL supplied does not prove the agency holds the listed records.',
    'Verify applicable fees, exclusions, local law and response deadlines yourself.',
    'Send manually through the approved agency channel, then record the actual submission date.'
   ],submitted:false,source_verified_by_software:false,caveat:spec.caveat});
 }
 function followUp(request,outcome,summary=''){
  if(!request||!line(request.subject,200))throw Error('Choose a saved request');
  if(request.status==='draft')throw Error('Mark the original request as sent before preparing a response follow-up');
  const kind=OUTCOMES[outcome];if(!kind)throw Error('Choose a response classification');
  const subject=line(request.subject,150);
  const recipient=line(request.recipient,200)||'Records custodian (recipient to confirm)';
  const s=line(summary,800);
  const content=[
   'UNSENT FOLLOW-UP — confirm the actual response, status and any applicable deadlines.',
   'To: '+recipient,'Subject: Follow-up: '+subject,'',
   'I am following up on my earlier records request titled "'+subject+'".',
   request.sent_on?'My recorded submission date: '+request.sent_on+'.':'Original request date: [confirm].',
   s?'My understanding of the response (researcher summary, not independently authenticated): '+s:'',
   '',kind.next,'',
   'I do not request individual license-plate records, private movement histories or restricted operational data.',
   'Please provide existing, reasonably segregable public records if held. This follow-up does not assume any legal violation, right to appeal or statutory deadline.',
   'Thank you.'
  ].join('\n');
  return Object.freeze({subject:('Follow-up: '+subject).slice(0,200),recipient,body:content,
   category:outcome,check_before_sending:[
    'Review the actual agency response. Classification is selected by the researcher, not automatically verified.',
    kind.next_action,
    'Verify any fees, exemption, administrative review or jurisdiction-specific deadline independently.',
    'Save as a new unsent draft; original response status and follow-up dates must be recorded separately.'
   ],submitted:false,original_request_id:request.id||null});
 }
 return Object.freeze({RECORD_TYPES,OUTCOMES,draft,followUp,safeUrl,isoDate,cost});
});
