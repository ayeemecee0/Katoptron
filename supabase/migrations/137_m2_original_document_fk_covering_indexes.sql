-- 137: Close new M2 source-discovery foreign-key covering-index advisories.
-- Existing primary keys are (page, document) and (document) respectively;
-- they do not cover the referencing FK sequences.
create index if not exists m2_original_link_observations_document_fk_idx
 on public.flock_original_document_link_observations(document_url);
create index if not exists m2_original_content_review_receipt_version_fk_idx
 on public.flock_original_document_content_review_receipts(document_url,content_sha256);
