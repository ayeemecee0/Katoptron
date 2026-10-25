-- Official public maps establish a documented agency Flock programme, not
-- GIS-verified individual coordinates. A local migration regression must
-- preserve that trust boundary and record the original government sources.
DO $$
DECLARE programme_count integer;
DECLARE camera_count integer;
BEGIN
  SELECT count(*) INTO programme_count
  FROM public.flock_documented_programs
  WHERE program_key IN ('apache_junction_az','alexandria_va')
    AND record_status='verified'
    AND program_status='documented_at_source_date'
    AND source_date <= current_date
    AND reported_camera_count IS NULL
    AND official_evidence_url LIKE 'https://%'
    AND official_claim_summary ILIKE '%map%';
  IF programme_count<>2 THEN
    RAISE EXCEPTION 'Government cartographic program provenance missing';
  END IF;
  SELECT count(*) INTO camera_count FROM public.flock_camera_locations
  WHERE jurisdiction_label IN ('Apache Junction, AZ','Alexandria, VA');
  IF camera_count<>0 THEN
    RAISE EXCEPTION 'Static map symbols must not be auto-promoted as exact GIS camera points';
  END IF;
  IF NOT (SELECT relrowsecurity FROM pg_class
    WHERE oid='public.flock_documented_programs'::regclass) THEN
    RAISE EXCEPTION 'Documented program RLS disabled';
  END IF;
  RAISE NOTICE 'Original-government static map program classification PASS';
END $$;
