/* Private case files. Browser has ONLY public Supabase key and user JWT.
   Every database and Storage operation is authorized again by server-side RLS. */
(function(root,factory){
 'use strict';const util=factory();if(typeof module==='object'&&module.exports)module.exports=util;
 if(root){root.KatoptronResearchUtils=util;if(root.document)root.addEventListener('DOMContentLoaded',()=>start(root,util));}
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 function sourceUrl(url){try{const p=new URL(url);return p.protocol==='https:'&&!p.username&&!p.password&&!p.hash&&p.hostname&&p.hostname.length>=5&&p.port===''?p.href:null;}catch{return null;}}
 function agencyKey(v){return typeof v==='string'&&/^[a-z0-9][a-z0-9 -]{1,120}\|[A-Z]{2}$/.test(v)?v:null;}
 function exportData(workspace,entry,requests,notes,files){
  return {schema_version:1,generated_utc:new Date().toISOString(),scope:'private_case_export_not_independently_verified_legal_or_operational_evidence',
    workspace:{id:workspace.id,title:workspace.title},
    case:{id:entry.id,agency_key:entry.agency_key,title:entry.title,status:entry.status},
    public_records_requests:requests.map(x=>({subject:x.subject,recipient:x.recipient,body:x.body,status:x.status,sent_on:x.sent_on,response_due_on:x.response_due_on,response_received_on:x.response_received_on})),
    notes:notes.map(x=>({note:x.note,source_url:sourceUrl(x.source_url),created_at:x.created_at})),
    attachments_metadata_only:files.map(x=>({filename:x.filename,file_size:x.file_size,created_at:x.created_at})),
    warning:'Attachment bytes are NOT included. Exported statements are not automatically verified; inspect each original source.'};
 }
 return Object.freeze({sourceUrl,agencyKey,exportData});
});
async function start(win,U){
 'use strict';
 const $=id=>win.document.getElementById(id);
 const el=(tag,value)=>{const x=win.document.createElement(tag);if(value!==undefined)x.textContent=String(value);return x;};
 const cfg=win.KATOPTRON_CONFIG;
 if(!cfg?.supabaseUrl||!cfg?.supabasePublishableKey||!win.supabase){
  $('status').textContent='Account service unavailable';return;
 }
 const sb=win.supabase.createClient(cfg.supabaseUrl,cfg.supabasePublishableKey);
 let user=null,workspaces=[],cases=[],selectedW=null,selectedC=null,detail={requests:[],notes:[],files:[]},membershipRole='viewer';
 const status=text=>{$('status').textContent=text};
 const unwrap=({data,error})=>{if(error)throw Error(error.message);return data};
 const msg=err=>{status('Action not completed: '+(err?.message||'Unexpected error'))};
 const addLink=(box,url,title)=>{const safe=U.sourceUrl(url);if(!safe)return;const a=el('a',title);a.href=safe;a.target='_blank';a.rel='noopener noreferrer';box.append(a);};
 const button=(title,fn)=>{const b=el('button',title);b.type='button';b.addEventListener('click',()=>Promise.resolve().then(fn).catch(msg));return b};
 const row=(title,children)=>{const d=el('article');d.className='card';d.append(el('h3',title));for(const child of children)d.append(child);return d;};
 const field=(title,value,type='text')=>{const label=el('label',title);const x=el('input');x.type=type;x.value=value||'';label.append(x);return [label,x];};
 const writable=()=>selectedW&&(selectedW.owner_id===user.id||membershipRole==='editor');
 function fileDownload(name,data,mime='application/json'){
  const blob=data instanceof Blob?data:new Blob([typeof data==='string'?data:JSON.stringify(data,null,2)],{type:mime});
  const url=URL.createObjectURL(blob);const a=el('a');a.href=url;a.download=name;win.document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),3000);
 }
 async function auth(){
  const session=await sb.auth.getUser();
  if(session.error && session.error.name!=='AuthSessionMissingError')throw Error(session.error.message);
  user=session.data?.user||null;
  if(!user){$('signin').hidden=false;$('workspaceApp').hidden=true;status('Sign in to access private investigations.');return;}
  if(!user.email_confirmed_at){$('signin').hidden=false;$('workspaceApp').hidden=true;status('Email confirmation required before using the research workspace.');return;}
  $('signin').hidden=true;$('workspaceApp').hidden=false;$('account').textContent=user.email||'Confirmed account';
  const token=new URL(win.location.href).searchParams.get('invite');
  if(token){
   try{
    const w=unwrap(await sb.rpc('research_accept_invite',{invite_token:token}));
    status('Private research workspace invite accepted.');
    const u=new URL(win.location.href);u.searchParams.delete('invite');win.history.replaceState(null,'',u);
   }catch(e){status('Invite could not be accepted: '+e.message)}
  }
  await loadWorkspaces();
 }
 async function loadWorkspaces(){
  workspaces=unwrap(await sb.from('research_workspaces').select('id,owner_id,title,created_at').order('created_at',{ascending:false}).limit(100));
  const select=$('workspaceSelect');const old=select.value;select.replaceChildren();
  select.append(new Option('Choose a workspace',''));
  for(const w of workspaces)select.append(new Option(w.title,w.id));
  select.value=workspaces.some(w=>w.id===old)?old:workspaces[0]?.id||'';
  await chooseWorkspace();
 }
 async function refreshMembers(){
  $('members').replaceChildren();
  if(!selectedW||selectedW.owner_id!==user.id)return;
  const members=unwrap(await sb.rpc('research_list_collaborators',{p_workspace:selectedW.id}));
  if(!members.length){$('members').append(el('small','No collaborators have accepted an invite.'));return;}
  $('members').append(el('h3','Active collaborators'));
  for(const m of members){
   const item=el('div');item.className='row';
   item.append(el('span',m.member_role+' · member '+m.member_id.slice(0,8)+'…'));
   item.append(button('Set viewer',async()=>{
    unwrap(await sb.rpc('research_change_collaborator_role',{p_workspace:selectedW.id,p_user:m.member_id,p_role:'viewer'}));
    await refreshMembers();status('Member is now read-only.');
   }));
   item.append(button('Set editor',async()=>{
    unwrap(await sb.rpc('research_change_collaborator_role',{p_workspace:selectedW.id,p_user:m.member_id,p_role:'editor'}));
    await refreshMembers();status('Member can now edit workspace cases.');
   }));
   item.append(button('Revoke access',async()=>{
    if(!win.confirm('Revoke this collaborator from this workspace?'))return;
    unwrap(await sb.rpc('research_remove_collaborator',{p_workspace:selectedW.id,p_user:m.member_id}));
    await refreshMembers();status('Collaboration access revoked.');
   }));
   $('members').append(item);
  }
 }
 async function deletePrivateCase(entry,workspace){
  if(workspace.owner_id!==user.id)throw Error('Only the original workspace owner can delete case files.');
  const prefix=workspace.id+'/'+entry.id+'/';
  let scans=0;
  while(scans++<40){
   const objects=unwrap(await sb.storage.from('research-case-files').list(prefix,{limit:100,offset:0}));
   if(!objects.length)break;
   if(objects.some(x=>!x.name||!x.id))throw Error('Storage folder contains unexpected nested entries; deletion held.');
   const files=objects.map(x=>prefix+x.name);
   unwrap(await sb.storage.from('research-case-files').remove(files));
  }
  if(scans>40)throw Error('Too many attachments to safely remove in one operation.');
  // SQL trigger independently rejects any case deletion while blobs remain.
  const found=unwrap(await sb.storage.from('research-case-files').list(prefix,{limit:1,offset:0}));
  if(found.length)throw Error('Storage cleanup not yet complete. Case metadata retained.');
  const removed=unwrap(await sb.from('research_cases').delete().eq('id',entry.id).eq('workspace_id',workspace.id).select('id'));
  if(removed.length!==1)throw Error('Case not deleted: ownership or concurrent change rejected.');
 }
 $('deleteCase').addEventListener('click',async()=>{
  try{
   if(!selectedC||selectedW.owner_id!==user.id)throw Error('Only workspace owner can permanently delete cases.');
   if(!win.confirm('Delete this case, its private files, requests, and notes? This cannot be undone.'))return;
   const old=selectedC;await deletePrivateCase(old,selectedW);
   await chooseWorkspace();status('Private case, response attachments, drafts and notes deleted.');
  }catch(e){msg(e)}
 });
 $('deleteWorkspace').addEventListener('click',async()=>{
  try{
   if(!selectedW||selectedW.owner_id!==user.id)throw Error('Only workspace owner can delete the workspace.');
   if(!win.confirm('Permanently delete ALL cases, private responses, collaboration and requests in this workspace?'))return;
   const w=selectedW;
   for(let pass=0;pass<60;pass++){
    const rows=unwrap(await sb.from('research_cases').select('id').eq('workspace_id',w.id).limit(100));
    if(!rows.length)break;
    for(const c of rows)await deletePrivateCase(c,w);
    if(pass===59)throw Error('Workspace deletion paused after too many case batches.');
   }
   const removed=unwrap(await sb.from('research_workspaces').delete().eq('id',w.id).select('id'));
   if(removed.length!==1)throw Error('Workspace deletion was blocked; remaining data stays private.');
   await loadWorkspaces();status('Workspace and all privately stored case files deleted.');
  }catch(e){msg(e)}
 });
 async function chooseWorkspace(){
  selectedW=workspaces.find(w=>w.id===$('workspaceSelect').value)||null;
  selectedC=null;cases=[];$('caseDetail').hidden=true;$('inviteResult').textContent='';
  $('createCase').hidden=!selectedW;
  $('collaboration').hidden=!selectedW||selectedW.owner_id!==user.id;
  $('deleteWorkspace').hidden=!selectedW||selectedW.owner_id!==user.id;
  if(!selectedW){$('caseSelect').replaceChildren(new Option('Create a workspace first',''));return;}
  membershipRole=selectedW.owner_id===user.id?'owner':(unwrap(await sb.from('research_workspace_members').select('role').eq('workspace_id',selectedW.id).eq('user_id',user.id).maybeSingle())?.role||'viewer');
  $('createCase').hidden=!writable();
  await refreshMembers();
  cases=unwrap(await sb.from('research_cases').select('id,title,agency_key,status,created_at,workspace_id').eq('workspace_id',selectedW.id).order('created_at',{ascending:false}).limit(200));
  const select=$('caseSelect'),old=select.value;select.replaceChildren(new Option('Choose a case',''));
  for(const c of cases)select.append(new Option(c.title+' · '+c.status,c.id));
  const initial=new URL(win.location.href).searchParams.get('case');
  select.value=cases.some(c=>c.id===initial)?initial:cases.some(c=>c.id===old)?old:cases[0]?.id||'';
  await chooseCase();
 }
 async function chooseCase(){
  selectedC=cases.find(c=>c.id===$('caseSelect').value)||null;
  $('caseDetail').hidden=!selectedC;if(!selectedC)return;
  $('caseHeading').textContent=selectedC.title;
  $('caseAgency').textContent=selectedC.agency_key+' · Case ID '+selectedC.id;
  $('caseStatus').value=selectedC.status;
  for(const id of ['saveStage','createRequest','addNote','uploadFile','upload'])$(id).disabled=!writable();
  $('deleteCase').hidden=selectedW.owner_id!==user.id;
  $('createRequest').hidden=!writable();$('addNote').hidden=!writable();
  let [r,n,f]=await Promise.all([
   sb.from('research_case_requests').select('*').eq('case_id',selectedC.id).order('created_at',{ascending:false}).limit(100),
   sb.from('research_case_notes').select('*').eq('case_id',selectedC.id).order('created_at',{ascending:false}).limit(100),
   sb.from('research_case_files').select('*').eq('case_id',selectedC.id).order('created_at',{ascending:false}).limit(100)]);
  detail={requests:unwrap(r),notes:unwrap(n),files:unwrap(f),history:[]};
  if(detail.requests.length){
   const ids=detail.requests.map(x=>x.id);
   detail.history=unwrap(await sb.from('research_request_activity')
    .select('request_id,previous_status,new_status,previous_due_on,new_due_on,action_at')
    .in('request_id',ids).order('action_at',{ascending:false}).limit(150));
  }
  renderDetails();
 }
 function renderDetails(){
  for(const id of ['requests','notes','files'])$(id).replaceChildren();
  for(const req of detail.requests){
   const [recipient,rinput]=field('Records custodian',req.recipient);
   const [subject,sinput]=field('Subject',req.subject);
   const body=el('textarea');body.value=req.body;
   const statusSel=el('select');
   for(const k of ['draft','sent','awaiting_response','received','closed'])statusSel.append(new Option(k.replaceAll('_',' '),k));
   statusSel.value=req.status;
   const dates=['sent_on','response_due_on','response_received_on'].map(k=>{
    const [label,x]=field(k.replaceAll('_',' '),req[k]||'','date');return [k,label,x];
   });
   const due=el('small');
   if(req.response_due_on&& !['received','closed'].includes(req.status)){
    const end=new Date(req.response_due_on+'T00:00:00Z');
    const today=new Date().toISOString().slice(0,10);
    const distance=Math.round((end.getTime()-Date.parse(today+'T00:00:00Z'))/86400000);
    due.textContent=distance<0?'User-entered follow-up date overdue by '+Math.abs(distance)+' day(s).':
      'User-entered follow-up in '+distance+' day(s). No statutory deadline inferred.';
   }
   const history=el('div');
   const audit=(detail.history||[]).filter(h=>h.request_id===req.id).slice(0,10);
   for(const h of audit)history.append(el('small',
    'Recorded '+String(h.action_at).slice(0,16)+' UTC: '+h.previous_status+' → '+h.new_status+
    (h.new_due_on?' · follow-up '+h.new_due_on:'')+'\n'));
   if(!audit.length)history.append(el('small','No status or date edits recorded yet.'));
   const content=[due,history,subject,recipient,el('label','Request body'),body,el('label','Status'),statusSel,...dates.map(x=>x[1])];
   if(writable())content.push(button('Save request and dates',async()=>{
    unwrap(await sb.from('research_case_requests').update({recipient:rinput.value,subject:sinput.value,body:body.value,status:statusSel.value,
      sent_on:dates[0][2].value||null,response_due_on:dates[1][2].value||null,response_received_on:dates[2][2].value||null,
      updated_at:new Date().toISOString()}).eq('id',req.id));
    status('Records request saved. Dates are user-entered, not inferred.');await chooseCase();
   }));
   $('requests').append(row(req.subject,content));
  }
  if(!detail.requests.length)$('requests').append(el('p','No requests yet. Save a draft to begin tracking.'));
  for(const n of detail.notes){
   const p=el('p',n.note),date=el('small',new Date(n.created_at).toLocaleDateString());
   const box=row('Research note',[date,p]);addLink(box,n.source_url,'Inspect original source');$('notes').append(box);
  }
  if(!detail.notes.length)$('notes').append(el('p','No research notes yet.'));
  for(const f of detail.files){
   const box=row(f.filename,[el('small',Math.ceil(f.file_size/1024)+' KB · private storage')]);
   box.append(button('Download privately',async()=>{
    const blob=unwrap(await sb.storage.from('research-case-files').download(f.storage_path));
    fileDownload(f.filename,blob);
    status('Private file downloaded to your device.');
   }));
   if(writable()&&(f.uploaded_by===user.id||selectedW.owner_id===user.id)){
    box.append(button('Delete attachment',async()=>{
      if(!win.confirm('Permanently remove this stored attachment?'))return;
      unwrap(await sb.storage.from('research-case-files').remove([f.storage_path]));
      unwrap(await sb.from('research_case_files').delete().eq('id',f.id));
      await chooseCase();status('Private response attachment deleted.');
    }));
   }
   $('files').append(box);
  }
  if(!detail.files.length)$('files').append(el('p','No government response files uploaded.'));
 }
 $('login').addEventListener('submit',async e=>{e.preventDefault();try{
  unwrap(await sb.auth.signInWithPassword({email:$('email').value.trim(),password:$('password').value}));
  $('password').value='';await auth();
 }catch(err){msg(err)}});
 $('register').addEventListener('click',async()=>{try{
  unwrap(await sb.auth.signUp({email:$('email').value.trim(),password:$('password').value,
   options:{emailRedirectTo:win.location.origin+win.location.pathname}}));
  $('password').value='';status('Check your email and confirm the account before signing in.');
 }catch(err){msg(err)}});
 $('signout').addEventListener('click',async()=>{try{unwrap(await sb.auth.signOut());user=null;await auth()}catch(e){msg(e)}});
 $('createWorkspace').addEventListener('submit',async e=>{e.preventDefault();try{
  if(!user)throw Error('Sign in');
  const w=unwrap(await sb.from('research_workspaces').insert({owner_id:user.id,title:$('workspaceTitle').value.trim()}).select('id').single());
  await loadWorkspaces();$('workspaceSelect').value=w.id;await chooseWorkspace();$('workspaceTitle').value='';
  status('Private workspace created.');
 }catch(err){msg(err)}});
 $('workspaceSelect').addEventListener('change',()=>chooseWorkspace().catch(msg));
 $('caseSelect').addEventListener('change',()=>chooseCase().catch(msg));
 function chosenTemplate(){
  const role=$('templateRole').value;
  if(!role)return null;
  if(!win.KatoptronResearchTemplates)throw Error('Research templates unavailable');
  return win.KatoptronResearchTemplates.draft(role,$('agencyKey').value,$('noteSource').value);
 }
 $('templatePreview').addEventListener('click',()=>{
  try{
   const d=chosenTemplate();
   if(!d){$('templateStatus').textContent='Blank investigation selected.';return;}
   $('caseTitle').value=d.title.slice(0,180);
   $('requestSubject').value=d.subject;
   $('requestBody').value=d.body;
   $('noteText').value=d.questions.map((x,i)=>(i+1)+'. '+x).join('\\n');
   $('templateStatus').textContent=d.label+' workflow prepared. Creating a case will save its editable records-request draft and source-checklist note.';
  }catch(e){msg(e)}
 });
 $('createCase').addEventListener('submit',async e=>{e.preventDefault();try{
  if(!writable())throw Error('Editor access required');
  const key=$('agencyKey').value.trim();
  if(key.length<3||key.length>160)throw Error('Enter an exact agency label/key');
  const template=chosenTemplate();
  const caseTitle=$('caseTitle').value.trim();
  const noteSource=U.sourceUrl($('noteSource').value.trim());
  const record=unwrap(await sb.from('research_cases').insert({workspace_id:selectedW.id,created_by:user.id,
   title:caseTitle,agency_key:key}).select('id').single());
  let generated=false;
  if(template){
   try{
    unwrap(await sb.from('research_case_requests').insert({case_id:record.id,created_by:user.id,
      subject:$('requestSubject').value.trim()||template.subject,
      body:$('requestBody').value||template.body,recipient:'',status:'draft'}));
    unwrap(await sb.from('research_case_notes').insert({case_id:record.id,author_id:user.id,
      note:('Research workflow: '+template.label+'\\n'+template.questions.map((q,i)=>(i+1)+'. '+q).join('\\n')).slice(0,5000),
      source_url:noteSource}));
    generated=true;
   }catch(e){status('Case created but template checklist or draft requires review: '+e.message)}
  }
  await chooseWorkspace();$('caseSelect').value=record.id;await chooseCase();$('caseTitle').value='';
  if(!template||generated)status(generated?'Case, editable request and research checklist saved. No public-records request was sent.':'Investigation created.');
 }catch(err){msg(err)}});
 $('saveStage').addEventListener('click',async()=>{try{
  if(!writable())throw Error('Editor access required');
  unwrap(await sb.from('research_cases').update({status:$('caseStatus').value,updated_at:new Date().toISOString()}).eq('id',selectedC.id));
  await chooseWorkspace();status('Case stage saved.');
 }catch(err){msg(err)}});
 $('createRequest').addEventListener('submit',async e=>{e.preventDefault();try{
  if(!writable())throw Error('Editor access required');
  unwrap(await sb.from('research_case_requests').insert({case_id:selectedC.id,created_by:user.id,
   recipient:$('requestRecipient').value,subject:$('requestSubject').value.trim(),body:$('requestBody').value}));
  $('requestBody').value='';await chooseCase();status('Editable public-records request saved as draft. No email sent.');
 }catch(err){msg(err)}});
 $('addNote').addEventListener('submit',async e=>{e.preventDefault();try{
  if(!writable())throw Error('Editor access required');
  const raw=$('noteSource').value.trim(),source=raw?U.sourceUrl(raw):null;
  if(raw&&!source)throw Error('Only original HTTPS source URLs are accepted');
  unwrap(await sb.from('research_case_notes').insert({case_id:selectedC.id,author_id:user.id,note:$('noteText').value.trim(),source_url:source}));
  $('noteText').value='';$('noteSource').value='';await chooseCase();status('Research note saved with its source attribution.');
 }catch(err){msg(err)}});
 $('uploadFile').addEventListener('click',async()=>{try{
  if(!writable())throw Error('Editor access required');
  const file=$('upload').files?.[0];
  if(!file||file.size>10485760||file.size===0||!['application/pdf','text/plain','image/jpeg','image/png'].includes(file.type))throw Error('Select a PDF, text or image response under 10 MB');
  const filename=file.name.replace(/[^a-zA-Z0-9._-]/g,'_').slice(0,150)||'response';
  const path=selectedW.id+'/'+selectedC.id+'/'+crypto.randomUUID()+'-'+filename;
  unwrap(await sb.storage.from('research-case-files').upload(path,file,{upsert:false,contentType:file.type}));
  try{
   unwrap(await sb.from('research_case_files').insert({case_id:selectedC.id,uploaded_by:user.id,
    storage_path:path,filename:file.name.slice(0,180),file_size:file.size}));
  }catch(e){await sb.storage.from('research-case-files').remove([path]);throw e;}
  $('upload').value='';await chooseCase();status('Private government response uploaded. Files are not publicly published or automatically verified.');
 }catch(e){msg(e)}});
 $('exportCase').addEventListener('click',()=>{
  if(!selectedC)return;
  fileDownload('katoptron-case-'+selectedC.id+'.json',U.exportData(selectedW,selectedC,detail.requests,detail.notes,detail.files));
 });
 $('printCase').addEventListener('click',()=>win.print());
 $('shareInvite').addEventListener('click',async()=>{try{
  if(selectedW.owner_id!==user.id)throw Error('Only owner can issue collaboration invitations');
  const invite=unwrap(await sb.from('research_workspace_invites').insert({workspace_id:selectedW.id,
   created_by:user.id,role:$('inviteRole').value}).select('token').single());
  const u=new URL(win.location.origin+win.location.pathname);u.searchParams.set('invite',invite.token);
  $('inviteResult').textContent='One-use invite (7 days): '+u.href;
  try{await win.navigator.clipboard.writeText(u.href);$('inviteResult').textContent+=' · link copied.';}catch{}
 }catch(e){msg(e)}});
 // Support prefilled exact-government agency research without publishing notes.
 const q=new URL(win.location.href).searchParams;
 if(q.has('agency'))$('agencyKey').value=q.get('agency').slice(0,160);
 if(q.has('title'))$('caseTitle').value=q.get('title').slice(0,180);
 if(q.has('source'))$('noteSource').value=U.sourceUrl(q.get('source'))||'';
 try{await auth()}catch(e){msg(e)}
}
