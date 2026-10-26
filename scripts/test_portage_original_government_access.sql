do $portage$
begin
 if not exists(
  select 1 from public.flock_original_sharing_sources
   where source_key='portage_in_original_government'
     and source_agency_id='portage-in-pd'
     and source_kind='original_government'
     and captured_scope='published_list_excerpt'
     and source_url='https://portagein.gov/547/Flock-Information-Center'
 ) then raise exception 'Original Portage city Flock source missing or overclaimed complete';end if;
 if (select count(*) from public.flock_original_sharing_edges where
  source_key='portage_in_original_government')<>7
 then raise exception 'Original government Portage named list incomplete';end if;
 if exists(select 1 from public.flock_original_sharing_edges
  where source_key='portage_in_original_government'
   and recipient_source_agency_id is null and identity_basis<>'unresolved_original_publisher_label')
 then raise exception 'Unresolved recipient falsely linked';end if;
 if (select count(*) from public.flock_original_sharing_edges)<202
 then raise exception 'Original publisher evidence inventory regressed';end if;
end $portage$;
