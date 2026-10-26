-- Opt-in email privacy, original-source-only Watch and secondary directory gates.
do $watch_security$
begin
 if not (select relrowsecurity from pg_class where oid='public.flock_watch_subscriptions'::regclass)
 then raise exception 'Private watched localities have no RLS';end if;
 if has_table_privilege('anon','public.flock_watch_subscriptions','SELECT')
   or has_table_privilege('anon','public.flock_watch_deliveries','SELECT')
   or has_table_privilege('authenticated','public.flock_watch_deliveries','SELECT')
 then raise exception 'Watch private email or receipts leaked';end if;
 if has_function_privilege('anon','public.flock_watch_delivery_candidates()','EXECUTE')
   or has_function_privilege('authenticated','public.flock_watch_delivery_candidates()','EXECUTE')
 then raise exception 'Private confirmed account recipient list exposed';end if;
 if not has_function_privilege('service_role','public.flock_watch_delivery_candidates()','EXECUTE')
 then raise exception 'Service-only mailer cannot inspect user-confirmed subscriptions';end if;
 if not has_table_privilege('anon','public.flock_secondary_portal_agencies','SELECT')
 then raise exception 'Licensed secondary agency directory unavailable';end if;
 if has_table_privilege('anon','public.flock_secondary_portal_agencies','UPDATE')
   or has_table_privilege('authenticated','public.flock_secondary_portal_agencies','INSERT')
 then raise exception 'Nonowners can tamper with source provenance';end if;
 if not exists(select 1 from pg_class where oid='public.flock_public_signed_contract_end_dates'::regclass
    and reloptions @> ARRAY['security_invoker=true']::text[])
 then raise exception 'Reviewed contract end dates bypass RLS';end if;
 if exists(select 1 from public.flock_agency_watch_events where
      source_url not like 'https://%' or kind='sharing_list_changed'
        and evidence_tier<>'secondary_aggregated_portal_snapshot')
 then raise exception 'Watch event provenance insufficient';end if;
end $watch_security$;
