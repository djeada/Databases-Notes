CREATE DATABASE IF NOT EXISTS notes;

DROP TABLE IF EXISTS notes.events;

CREATE TABLE notes.events (
    event_time DateTime,
    user_id UInt64,
    country LowCardinality(String),
    event_type LowCardinality(String),
    revenue Decimal(12, 2)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_time)
ORDER BY (country, event_type, event_time);

INSERT INTO notes.events VALUES
('2026-09-29 10:00:00', 101, 'DE', 'view', 0),
('2026-09-29 10:01:00', 101, 'DE', 'purchase', 19.95),
('2026-09-30 09:00:00', 205, 'US', 'view', 0),
('2026-09-30 09:02:00', 205, 'US', 'purchase', 39.00),
('2026-09-30 09:05:00', 101, 'DE', 'view', 0);

SELECT
    country,
    event_type,
    count() AS events,
    sum(revenue) AS revenue,
    uniqExact(user_id) AS users
FROM notes.events
GROUP BY country, event_type
ORDER BY country, event_type;

SELECT
    partition,
    name,
    rows
FROM system.parts
WHERE database = 'notes'
  AND table = 'events'
  AND active
ORDER BY partition, name;
