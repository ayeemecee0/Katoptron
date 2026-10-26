-- 134: Additional independently checked first-party government statement.
-- The date is PUBLICATION date only; Salem gave no specific contract end,
-- removal completion, executed cost or individual council vote in this post.
insert into public.flock_original_civic_milestones
(milestone_key,jurisdiction_label,event_type,event_date,date_basis,title,summary,
 source_url,amount_usd,amount_basis,source_reviewed_on)
values (
 'salem_ma_flock_nonrenewal_statement_2026_07_23',
 'Salem, MA','government_disclosure_publication','2026-07-23',
 'original_city_reported_publication_date',
 'Salem announced Flock Safety contract nonrenewal and planned ALPR replacement',
 'The City of Salem and its police department published an original statement on July 23, 2026 reporting that Salem would not renew its existing Flock Safety contract and planned to replace Flock automatic license plate readers. This is a dated original city statement of intent. The post does NOT establish the actual contract expiration day, equipment removal completion, current permission status, replacement vendor contract, or any individual council vote.',
 'https://www.salemma.gov/m/NewsFlash/Home/Detail/427',
 null,null,'2026-10-25'
) on conflict(milestone_key) do nothing;
