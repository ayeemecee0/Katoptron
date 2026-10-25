do $$
declare st text;
begin
 foreach st in array array['CA','TX','WA','FL','AZ'] loop
  if not exists (
    select 1 from public.flock_public_state_evidence_index
    where state_code=st and vendor_disclosed_agencies > 0
  ) then raise exception 'Missing separate first-party vendor coverage for %',st; end if;
 end loop;
 if (select vendor_disclosed_agencies from public.flock_public_state_evidence_index
      where state_code='CA') <> 9 then
  raise exception 'California vendor count must be distinct agencies, not cameras';
 end if;
 if (select sum(verified_camera_points) from public.flock_public_state_evidence_index)
   <> (select count(*) from public.flock_camera_locations
      where verification_status='verified' and location_accuracy='exact'
        and jurisdiction_label ~ ', [A-Z]{2}$') then
  raise exception 'Vendor coverage inflated georeferenced canonical cameras';
 end if;
 if not exists (select 1 from pg_class where
     oid='public.flock_public_state_evidence_index'::regclass
     and reloptions @> array['security_invoker=true']::text[]) then
  raise exception 'State footprint must respect underlying RLS as invoker';
 end if;
 raise notice 'State vendor footprint remains independent of exact GIS points PASS';
end $$;
