\set ON_ERROR_STOP on

\echo ''
\echo 'User index inventory:'

SELECT
    stats.schemaname,
    stats.relname AS table_name,
    stats.indexrelname AS index_name,
    pg_size_pretty(pg_relation_size(stats.indexrelid)) AS index_size,
    stats.idx_scan,
    index_meta.indisprimary AS is_primary,
    index_meta.indisunique AS is_unique,
    index_meta.indisvalid AS is_valid,
    (constraint_meta.oid IS NOT NULL) AS backs_constraint,
    pg_get_indexdef(stats.indexrelid) AS definition
FROM pg_stat_user_indexes AS stats
JOIN pg_index AS index_meta
  ON index_meta.indexrelid = stats.indexrelid
LEFT JOIN pg_constraint AS constraint_meta
  ON constraint_meta.conindid = stats.indexrelid
ORDER BY
    pg_relation_size(stats.indexrelid) DESC,
    stats.schemaname,
    stats.relname,
    stats.indexrelname;

\echo ''
\echo 'Important: idx_scan is only evidence from the current statistics window.'
\echo 'A low count does not prove an index is safe to drop.'
