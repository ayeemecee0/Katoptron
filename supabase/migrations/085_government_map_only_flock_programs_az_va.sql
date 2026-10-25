-- Original-government Flock programs with public *cartographic* location maps.
-- Static maps do not establish exact individual GIS point geometries.
-- Never convert symbols to a canonical camera point without independent
-- original-government verified GIS source and complete ObjectID inventory.
INSERT INTO public.flock_documented_programs
  (program_key,jurisdiction_label,state_code,program_status,
   official_evidence_url,official_claim_summary,source_date,
   reported_camera_count,record_status)
VALUES
  ('apache_junction_az','Apache Junction, AZ','AZ','documented_at_source_date',
   'https://apachejunctionaz.gov/1241/Public-Safety-Technology',
   'Apache Junction Police Department confirms use of Flock Safety ALPR cameras and links its official camera-location map. The map is a dated cartographic image, not a verified individual machine-readable GIS point inventory. Counts and current installation status may change; do not infer exact camera coordinates.',
   '2026-10-06',NULL,'verified'),
  ('alexandria_va','Alexandria, VA','VA','documented_at_source_date',
   'https://www.alexandriava.gov/police-department/license-plate-reader-dashboard-and-response-to-city-council-questions-on-flock',
   'The Alexandria Police Department documents its Flock Safety ALPR program and publishes a fixed ALPR camera street map, updated October 2026. The map is a static cartographic document: its symbols are not verified exact individual geographic coordinates and are not published as camera map pins.',
   '2026-10-15',NULL,'verified')
ON CONFLICT (program_key) DO NOTHING;
