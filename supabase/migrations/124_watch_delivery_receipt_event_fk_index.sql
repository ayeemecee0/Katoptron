-- 124: index delivery receipt's event-key foreign key.
-- Prevent full scans of private subscriber delivery receipts if public
-- source events are revoked under a valid evidence withdrawal.
create index if not exists flock_watch_deliveries_event_fk_idx
 on public.flock_watch_deliveries(event_key);
