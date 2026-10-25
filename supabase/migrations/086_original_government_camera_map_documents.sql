-- Official original-government cartographic ALPR maps.
-- Static maps are linked as documents; they do NOT certify GIS coordinates.
ALTER TABLE public.flock_documented_programs
  ADD COLUMN IF NOT EXISTS official_camera_map_url text;
ALTER TABLE public.flock_documented_programs
  ADD CONSTRAINT official_camera_map_same_original_host CHECK (
    official_camera_map_url IS NULL OR (
      length(official_camera_map_url) BETWEEN 20 AND 1900
      AND official_camera_map_url ~ '^https://[A-Za-z0-9.-]+/'
      AND split_part(official_camera_map_url,'/',3) =
          split_part(official_evidence_url,'/',3)
    )
  );
UPDATE public.flock_documented_programs
SET official_camera_map_url='https://apachejunctionaz.gov/DocumentCenter/View/33429'
WHERE program_key='apache_junction_az'
  AND official_evidence_url='https://apachejunctionaz.gov/1241/Public-Safety-Technology'
  AND record_status='verified';
UPDATE public.flock_documented_programs
SET official_camera_map_url='https://www.alexandriava.gov/sites/default/files/2026-10/ALPR%20cameras%20with%20streets%20(1).pdf'
WHERE program_key='alexandria_va'
  AND official_evidence_url='https://www.alexandriava.gov/police-department/license-plate-reader-dashboard-and-response-to-city-council-questions-on-flock'
  AND record_status='verified';
COMMENT ON COLUMN public.flock_documented_programs.official_camera_map_url
IS 'Original agency-hosted public cartographic camera-location map link; never evidence of individually verified machine-readable georeferenced camera points.';
