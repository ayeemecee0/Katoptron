-- DISPOSABLE CI-ONLY fixture. These rows represent the production source
-- checksum and scope but do not substitute for inspection of original PDF.
-- Never run this fixture against production or publish fake source content.
insert into public.flock_original_document_leads
(document_url,government_page_url,jurisdiction_label,document_class,link_label,source_page_sha256)
values(
'https://www.alexandriava.gov/sites/default/files/2025-10/10.40_license_plate_reader.pdf',
'https://www.alexandriava.gov/police-department/license-plate-reader-dashboard-and-response-to-city-council-questions-on-flock',
'Alexandria, VA','policy','Directive 10.40 License Plate Reader Program PDF',
repeat('a',64)
);
insert into public.flock_original_document_pdf_receipts
(document_url,content_sha256,byte_length,observed_media_type)
values(
'https://www.alexandriava.gov/sites/default/files/2025-10/10.40_license_plate_reader.pdf',
'83afdded0ea717a44a7969c1487e2a30bac1285c9d98c2f83622eabcfff05ea4',
1028198,'application/pdf'
);
insert into public.flock_original_pdf_content_triage
(document_url,content_sha256,pages_reported,pages_examined,triage_status,document_signal_flags)
values(
'https://www.alexandriava.gov/sites/default/files/2025-10/10.40_license_plate_reader.pdf',
'83afdded0ea717a44a7969c1487e2a30bac1285c9d98c2f83622eabcfff05ea4',
7,7,'readable_document_indicators_only','{}'::jsonb
);
