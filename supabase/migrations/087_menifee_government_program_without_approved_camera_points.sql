-- Menifee PD Flock programme: official agency disclosure, no verified camera pins.
-- Publisher-linked municipal Esri camera layer remains a separate private
-- research candidate pending express layer-source authority / source review.
INSERT INTO public.flock_documented_programs (
  program_key,jurisdiction_label,state_code,program_status,
  official_evidence_url,official_claim_summary,source_date,
  reported_camera_count,record_status
) VALUES (
  'menifee_ca','Menifee, CA','CA','documented_at_source_date',
  'https://menifeepolice.org/automated-licesnse-plate-reader/',
  'The original Menifee Police Department ALPR program page confirms use of Flock Safety technology and describes retroactive searches and real-time hotlist alerts. A separate city-affiliated ArcGIS service contains a Flock Cameras point layer, but its 27 GIS features have not been independently authorized as a publicly verified location inventory; no exact camera coordinates or current operation are inferred from this program record.',
  '2026-10-24',NULL,'verified'
)
ON CONFLICT (program_key) DO NOTHING;
