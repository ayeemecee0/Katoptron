-- First-party sharing evidence RLS, matching and provenance acceptance.
do $verify$
declare n integer;
begin
 if not exists(select 1 from pg_class
   where oid='public.flock_public_original_sharing_evidence'::regclass
     and reloptions @> ARRAY['security_invoker=true']::text[])
 then raise exception 'First-party sharing view could bypass RLS';end if;
 if has_table_privilege('anon','public.flock_original_sharing_edges','INSERT')
  or has_table_privilege('authenticated','public.flock_original_sharing_edges','UPDATE')
 then raise exception 'Publisher-reported sharing evidence editable by public account';end if;
 if not has_table_privilege('anon','public.flock_public_original_sharing_evidence','SELECT')
 then raise exception 'Original published evidence unreadable';end if;
 select count(*) into n from public.flock_original_sharing_edges;
 if n<190 then raise exception 'Initial original sharing source evidence missing: %',n;end if;
 if not exists(select 1 from public.flock_original_sharing_edges e
     where e.source_key='elk_grove_original_government'
       and e.recipient_label='Folsom CA PD'
       and e.recipient_source_agency_id='folsom-ca-pd'
       and e.identity_basis='exact_source_agency_name')
 then raise exception 'Original government Elk Grove to Folsom direction not qualified';end if;
 if exists(select 1 from public.flock_original_sharing_edges e
   left join public.flock_secondary_portal_agencies p on p.source_agency_id=e.recipient_source_agency_id
   where (e.recipient_source_agency_id is null and e.identity_basis<>'unresolved_original_publisher_label')
    or (e.recipient_source_agency_id is not null and (
      e.identity_basis<>'exact_source_agency_name'
      or p.agency_name<>e.recipient_label)))
 then raise exception 'Non-exact original source recipient was silently upgraded to known agency';end if;
 if exists(select 1 from public.flock_public_original_sharing_evidence
    where source_kind not in ('original_government','original_flock_vendor_portal')
       or interpretation<>'publisher_listed_outbound_access_as_of_snapshot'
       or source_url not like 'https://%')
 then raise exception 'Publisher evidence credibility or direction boundary violated';end if;
end $verify$;
