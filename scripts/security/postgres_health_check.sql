\set ON_ERROR_STOP on

\echo ''
\echo 'Database identity and current time:'
SELECT
    current_database() AS database,
    current_user AS database_user,
    now() AS observed_at;

\echo ''
\echo 'Connections by state:'
SELECT
    COALESCE(state, '<none>') AS state,
    count(*) AS sessions
FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY state
ORDER BY sessions DESC, state;

\echo ''
\echo 'Transactions open longer than 30 seconds:'
SELECT
    pid,
    usename,
    application_name,
    state,
    now() - xact_start AS transaction_age,
    wait_event_type,
    wait_event
FROM pg_stat_activity
WHERE datname = current_database()
  AND xact_start IS NOT NULL
  AND now() - xact_start > interval '30 seconds'
  AND pid <> pg_backend_pid()
ORDER BY xact_start;

\echo ''
\echo 'Sessions currently waiting on locks:'
SELECT
    activity.pid,
    activity.usename,
    activity.application_name,
    now() - activity.query_start AS query_age,
    activity.wait_event_type,
    activity.wait_event
FROM pg_stat_activity AS activity
WHERE activity.datname = current_database()
  AND activity.wait_event_type = 'Lock'
ORDER BY activity.query_start;

\echo ''
\echo 'Database activity counters:'
SELECT
    datname,
    numbackends,
    xact_commit,
    xact_rollback,
    blks_read,
    blks_hit,
    temp_files,
    pg_size_pretty(temp_bytes) AS temp_bytes,
    deadlocks
FROM pg_stat_database
WHERE datname = current_database();

\echo ''
\echo 'Largest user tables:'
SELECT
    schemaname,
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    n_live_tup,
    n_dead_tup,
    seq_scan,
    idx_scan
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 20;

\echo ''
\echo 'Largest indexes and observed scan count:'
SELECT
    schemaname,
    relname AS table_name,
    indexrelname AS index_name,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;

\echo ''
\echo 'Optional next step: enable pg_stat_statements in a suitable test environment'
\echo 'to investigate normalized query frequency and cumulative execution time.'
