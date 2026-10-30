// A private archive gateway for trusted Katoptron main-branch GitHub Actions only.
// Deployed with verify_jwt=false because GitHub OIDC JWT is verified below instead.
import { createClient } from "jsr:@supabase/supabase-js@2";
import { createRemoteJWKSet, jwtVerify } from "jsr:@panva/jose@6";
const BUCKET = "katoptron-original-archive";
const AUD = "katoptron-originals-archive";
const SOURCE = "ayeemecee0/Katoptron";
const WORKFLOW = SOURCE + "/.github/workflows/watch_nationwide_government_originals.yml@refs/heads/main";
const jwks = createRemoteJWKSet(new URL("https://token.actions.githubusercontent.com/.well-known/jwks"));
const res = (status:number, data:unknown) => Response.json(data, {status, headers:{"Cache-Control":"no-store"}});
const id = /^[a-z0-9_-]{7,120}$/;
const hash = /^[a-f0-9]{64}$/;
const STATE_KEY = "state/backup-index.json";
const url = Deno.env.get("SUPABASE_URL");
const service = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
if (!url || !service) throw new Error("Required Supabase service environment is unavailable");
const admin = createClient(url, service, {auth:{autoRefreshToken:false,persistSession:false}});
Deno.serve(async (req:Request) => {
 if (req.method !== "POST") return res(405,{error:"method_not_allowed"});
 try {
  const bearer = req.headers.get("Authorization")?.match(/^Bearer ([A-Za-z0-9._-]+)$/)?.[1];
  if (!bearer) return res(401,{error:"github_oidc_required"});
  const {payload} = await jwtVerify(bearer,jwks,{
   issuer:"https://token.actions.githubusercontent.com",audience:AUD,algorithms:["RS256"]
  });
  const allowedSubject = "repo:ayeemecee0/Katoptron:ref:refs/heads/main";
  const immutableSubject = "repo:ayeemecee0@202164711/Katoptron@1427371008:ref:refs/heads/main";
  if (![allowedSubject,immutableSubject].includes(String(payload.sub)) ||
      payload.repository !== SOURCE || String(payload.repository_id)!=="1427371008" ||
      String(payload.repository_owner_id)!=="202164711" ||
      payload.ref!=="refs/heads/main" || payload.workflow_ref!==WORKFLOW ||
      !["push","schedule","workflow_dispatch"].includes(String(payload.event_name))) {
   return res(403,{error:"untrusted_workflow_identity"});
  }
  const body = await req.json();
  const action = body?.action;
  const isState = body?.state === true;
  const kind = body?.kind;
  const sid = body?.source_id;
  const sha = body?.sha256;
  if (body?.state !== true && body?.state !== false) return res(400,{error:"state_flag_required"});
  if (!isState && (!id.test(String(sid)) || !hash.test(String(sha)) ||
      !["html","pdf","json"].includes(kind))) return res(400,{error:"invalid_original_identity"});
  const objectKey = isState ? STATE_KEY : "originals/"+sid+"/"+sha+"."+kind;
  if (!["sign_upload","sign_download"].includes(action)) return res(400,{error:"unknown_action"});
  if (action === "sign_upload") {
   const {data,error}=await admin.storage.from(BUCKET).createSignedUploadUrl(objectKey,{upsert:isState});
   if (error || !data) return res(502,{error:"sign_upload_failed"});
   return res(200,{signed_url:data.signedUrl,object_key:objectKey});
  }
  const {data,error}=await admin.storage.from(BUCKET).createSignedUrl(objectKey,120);
  if (error || !data) return res(404,{error:"archived_original_not_found"});
  return res(200,{signed_url:data.signedUrl,object_key:objectKey});
 } catch (_e) {return res(401,{error:"authentication_or_request_rejected"});}
});
