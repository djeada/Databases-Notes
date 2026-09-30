CREATE KEYSPACE IF NOT EXISTS notes
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

CREATE TABLE IF NOT EXISTS notes.events_by_user (
    user_id text,
    event_time timestamp,
    event_id uuid,
    event_type text,
    payload text,
    PRIMARY KEY ((user_id), event_time, event_id)
) WITH CLUSTERING ORDER BY (event_time DESC);

TRUNCATE notes.events_by_user;

INSERT INTO notes.events_by_user
(user_id, event_time, event_id, event_type, payload)
VALUES
('user-42', '2026-09-30T20:00:00Z', 11111111-1111-1111-1111-111111111111, 'login', '{"device":"web"}');

INSERT INTO notes.events_by_user
(user_id, event_time, event_id, event_type, payload)
VALUES
('user-42', '2026-09-30T20:05:00Z', 22222222-2222-2222-2222-222222222222, 'view_product', '{"sku":"DB-101"}');

INSERT INTO notes.events_by_user
(user_id, event_time, event_id, event_type, payload)
VALUES
('user-99', '2026-09-30T20:07:00Z', 33333333-3333-3333-3333-333333333333, 'login', '{"device":"mobile"}');

SELECT *
FROM notes.events_by_user
WHERE user_id = 'user-42';
