CREATE KEYSPACE IF NOT EXISTS nosql_notes
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

CREATE TABLE IF NOT EXISTS nosql_notes.events_by_customer_month (
    customer_id text,
    bucket_month text,
    event_time timestamp,
    event_id uuid,
    event_type text,
    payload text,
    PRIMARY KEY (
        (customer_id, bucket_month),
        event_time,
        event_id
    )
) WITH CLUSTERING ORDER BY (event_time DESC);

TRUNCATE nosql_notes.events_by_customer_month;

INSERT INTO nosql_notes.events_by_customer_month
(customer_id, bucket_month, event_time, event_id, event_type, payload)
VALUES
('customer-42', '2026-10', '2026-10-01T12:00:00Z',
 11111111-1111-1111-1111-111111111111, 'login', '{"device":"web"}');

INSERT INTO nosql_notes.events_by_customer_month
(customer_id, bucket_month, event_time, event_id, event_type, payload)
VALUES
('customer-42', '2026-10', '2026-10-01T12:05:00Z',
 22222222-2222-2222-2222-222222222222, 'purchase', '{"order":"order-1001"}');

INSERT INTO nosql_notes.events_by_customer_month
(customer_id, bucket_month, event_time, event_id, event_type, payload)
VALUES
('customer-42', '2026-09', '2026-09-30T23:55:00Z',
 33333333-3333-3333-3333-333333333333, 'view', '{"sku":"DB-101"}');

SELECT *
FROM nosql_notes.events_by_customer_month
WHERE customer_id = 'customer-42'
  AND bucket_month = '2026-10'
LIMIT 50;
