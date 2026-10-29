(function(root,factory){
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronResearchTemplates=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const catalog=Object.freeze({
  journalist:{label:'Journalist',goal:'A source-cited timeline for publication',questions:[
   'Which official minutes, votes, and original records establish authorization?',
   'What records contradict or qualify the publisher announcement?',
   'What signed contracts and invoices document actual spending and dates?',
   'What official on-record response is available?',
   'Which facts remain unverified or disputed?']},
  nonprofit:{label:'Nonprofit',goal:'Accountability and policy evidence',questions:[
   'What current policy versions establish retention and external access?',
   'Where is the official governing-body approval and public oversight record?',
   'What aggregate audits document controls without personal plate data?',
   'How does the agency disclose complaints and privacy protections?',
   'What promised safeguards still lack documentary evidence?']},
  legal_researcher:{label:'Legal researcher',goal:'Indexed primary documents and provenance',questions:[
   'What signed contract versions and amendments exist, with dates?',
   'What original records establish policy adoption versus draft status?',
   'What public records show data retention, disclosure and access rules?',
   'What can be corroborated by government documents and page citations?',
   'What records were withheld, with stated reasons?']}
 });
 function draft(role,agency,source){
  const t=catalog[role];if(!t)throw Error('Unknown professional workflow');
  const name=String(agency||'').trim().slice(0,150)||'[named government agency]';
  const url=typeof source==='string'&&source.startsWith('https://')&&!/\s/.test(source)?source:null;
  return {role,label:t.label,goal:t.goal,
    title:name+' · '+t.goal,
    subject:'Original government ALPR / Flock records request',
    questions:t.questions.slice(),
    source_url:url,
    body:['To: Public Records Officer, '+name,
     'Subject: Original government ALPR / Flock records request',
     '','Please provide publicly releasable, existing records sufficient to answer:',
     ...t.questions.map((q,i)=>(i+1)+'. '+q),
     '','I do not request private license-plate observations, personal movement histories,',
     'hotlists, individual search logs or user credentials.',
     'Original government source: '+(url||'[Insert independently verified government source URL]'),
     'Please advise of fees. Applicable deadlines and local records law require independent confirmation.'].join('\n')
  };
 }
 return Object.freeze({catalog,draft});
});
