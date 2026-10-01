#!/usr/bin/env bash

set -euo pipefail

CONTAINER="${POSTGRES_CONTAINER:-postgres-local}"
ADMIN_USER="${POSTGRES_ADMIN_USER:-demo}"
DRILL_DB="security_restore_drill"
DUMP_PATH="/tmp/security_restore_drill.dump"

cleanup() {
  docker exec "$CONTAINER"     psql -U "$ADMIN_USER" -d postgres -v ON_ERROR_STOP=1     -c "DROP DATABASE IF EXISTS $DRILL_DB WITH (FORCE);"     >/dev/null || true

  docker exec "$CONTAINER" rm -f "$DUMP_PATH" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "Creating disposable database: $DRILL_DB"
cleanup
trap cleanup EXIT

docker exec "$CONTAINER"   psql -U "$ADMIN_USER" -d postgres -v ON_ERROR_STOP=1   -c "CREATE DATABASE $DRILL_DB;"   >/dev/null

docker exec "$CONTAINER"   psql -U "$ADMIN_USER" -d "$DRILL_DB" -v ON_ERROR_STOP=1 <<'SQL'
CREATE TABLE restore_probe (
    probe_id integer PRIMARY KEY,
    payload text NOT NULL
);

INSERT INTO restore_probe (probe_id, payload)
VALUES
    (1, 'alpha'),
    (2, 'bravo'),
    (3, 'charlie');
SQL

echo "Taking pg_dump..."
docker exec "$CONTAINER"   pg_dump -U "$ADMIN_USER" -d "$DRILL_DB"   -Fc -f "$DUMP_PATH"

echo "Destroying the disposable database..."
docker exec "$CONTAINER"   psql -U "$ADMIN_USER" -d postgres -v ON_ERROR_STOP=1   -c "DROP DATABASE $DRILL_DB WITH (FORCE);"   >/dev/null

echo "Recreating and restoring..."
docker exec "$CONTAINER"   psql -U "$ADMIN_USER" -d postgres -v ON_ERROR_STOP=1   -c "CREATE DATABASE $DRILL_DB;"   >/dev/null

docker exec "$CONTAINER"   pg_restore -U "$ADMIN_USER" -d "$DRILL_DB"   "$DUMP_PATH"

row_count="$(
  docker exec "$CONTAINER"     psql -U "$ADMIN_USER" -d "$DRILL_DB"     -Atc "SELECT count(*) FROM restore_probe;"
)"

checksum="$(
  docker exec "$CONTAINER"     psql -U "$ADMIN_USER" -d "$DRILL_DB"     -Atc "SELECT string_agg(probe_id || ':' || payload, ',' ORDER BY probe_id) FROM restore_probe;"
)"

if [[ "$row_count" != "3" ]]; then
  echo "Restore verification failed: expected 3 rows, got $row_count" >&2
  exit 1
fi

if [[ "$checksum" != "1:alpha,2:bravo,3:charlie" ]]; then
  echo "Restore verification failed: unexpected restored values: $checksum" >&2
  exit 1
fi

echo "Restore verified: 3 expected rows and values recovered."
echo "Cleanup will remove the disposable database and dump."
