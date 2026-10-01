\set ON_ERROR_STOP on

CREATE TEMP TABLE indexing_demo_events (
    event_id bigint PRIMARY KEY,
    event_time timestamptz NOT NULL,
    device_id integer NOT NULL,
    payload text NOT NULL
);

INSERT INTO indexing_demo_events(
    event_id,
    event_time,
    device_id,
    payload
)
SELECT
    g,
    TIMESTAMPTZ '2025-01-01 00:00:00+00'
        + g * INTERVAL '1 second',
    (g % 1000)::integer,
    'event-' || g
FROM generate_series(1, 300000) AS g;

ANALYZE indexing_demo_events;

CREATE INDEX idx_indexing_demo_events_btree
ON indexing_demo_events(event_time);

CREATE INDEX idx_indexing_demo_events_brin
ON indexing_demo_events
USING brin(event_time)
WITH (pages_per_range = 32);

ANALYZE indexing_demo_events;

\echo ''
\echo 'B-tree versus BRIN index size:'
SELECT
    relname AS index_name,
    pg_size_pretty(pg_relation_size(oid)) AS size
FROM pg_class
WHERE oid IN (
    'idx_indexing_demo_events_btree'::regclass,
    'idx_indexing_demo_events_brin'::regclass
)
ORDER BY pg_relation_size(oid) DESC;

\echo ''
\echo 'Plan while both indexes exist (planner can choose):'
EXPLAIN (COSTS OFF)
SELECT event_id, event_time
FROM indexing_demo_events
WHERE event_time >= TIMESTAMPTZ '2025-01-03 00:00:00+00'
  AND event_time <  TIMESTAMPTZ '2025-01-03 00:10:00+00';

DROP INDEX idx_indexing_demo_events_btree;

\echo ''
\echo 'Plan after removing the B-tree, leaving the BRIN summary index:'
EXPLAIN (COSTS OFF)
SELECT event_id, event_time
FROM indexing_demo_events
WHERE event_time >= TIMESTAMPTZ '2025-01-03 00:00:00+00'
  AND event_time <  TIMESTAMPTZ '2025-01-03 00:10:00+00';
