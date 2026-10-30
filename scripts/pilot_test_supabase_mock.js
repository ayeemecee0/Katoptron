/* Browser-only test double. Never loaded by the production site.
 * Models confirmed owner access to test the complete private import UI.
 * Real access isolation remains covered by PostgreSQL RLS integration tests.
 */
(()=>{'use strict';
 const id='11111111-1111-1111-1111-111111111111', tables={
  research_workspaces:[],research_cases:[],research_case_notes:[],research_case_requests:[],
  research_case_files:[],research_request_activity:[],research_workspace_members:[],
  research_workspace_invites:[],research_team_activity:[]
 };
 let counter=0;
 const stamp=()=>new Date(2026,9,29).toISOString();
 const uid=()=>String(++counter).padStart(8,'0')+'-aaaa-bbbb-cccc-111111111111';
 function table(name){
  if(!Object.prototype.hasOwnProperty.call(tables,name))throw Error('Unexpected private table '+name);
  let mode='select',filter=[],sort='',limit=Infinity,insertRows=[],selecting=false;
  const api={
   select(){selecting=true;return api},
   eq(key,value){filter.push(r=>r[key]===value);return api},
   is(key,value){filter.push(r=>r[key]===value);return api},
   gt(key,value){filter.push(r=>r[key]>value);return api},
   in(key,values){filter.push(r=>values.includes(r[key]));return api},
   order(key,opt){sort=key;return api},
   limit(n){limit=n;return api},
   insert(input){mode='insert';insertRows=(Array.isArray(input)?input:[input]).map(x=>({...x}));return api},
   delete(){mode='delete';return api},
   update(){throw Error('Unexpected update in pilot acceptance test')},
   single(){const out=execute();return Promise.resolve({...out,data:out.data[0]||null})},
   maybeSingle(){const out=execute();return Promise.resolve({...out,data:out.data[0]||null})},
   then(resolve,reject){return Promise.resolve(execute()).then(resolve,reject)}
  };
  let called=false;
  function execute(){
   if(called)throw Error('Query executed twice');
   called=true;let result;
   const data=tables[name];
   if(mode==='insert'){
    result=insertRows.map(r=>({...r,id:r.id||uid(),created_at:r.created_at||stamp(),updated_at:r.updated_at||stamp()}));
    data.push(...result);
   }else{
    result=data.filter(r=>filter.every(test=>test(r)));
    if(mode==='delete'){
     for(const r of result){const i=data.indexOf(r);if(i>=0)data.splice(i,1)}
    }
   }
   if(sort)result=result.slice().sort((a,b)=>String(b[sort]).localeCompare(String(a[sort])));
   return {data:result.slice(0,limit),error:null};
  }
  return api;
 }
 const user={id,email:'pilot-test@example.org',email_confirmed_at:'2026-10-29T01:00:00Z'};
 const client={
  auth:{
   getUser:async()=>({data:{user},error:null}),
   signOut:async()=>({data:{},error:null}),
   signInWithPassword:async()=>({data:{user},error:null}),
   signUp:async()=>({data:{user},error:null})
  },
  from:table,
  rpc:async(name)=>{if(name==='research_list_collaborators')return {data:[],error:null};throw Error('Unexpected RPC '+name)},
  storage:{from:()=>({})}
 };
 window.__pilotTestTables=tables;
 window.supabase={createClient:()=>client};
})();
