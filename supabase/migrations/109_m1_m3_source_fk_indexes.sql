-- M1/M3: index both recently introduced foreign-key joins used by
-- candidate-to-canonical reconciliation and per-source revocation.
-- No evidence classifications, RLS grants or publication records change.
create index if not exists flock_gis_disposition_original_public_fk_idx
on public.flock_gis_point_case_dispositions(original_public_record_key);
create index if not exists flock_attributed_point_source_fk_idx
on public.flock_source_attributed_map_points(source_key);
