\set ON_ERROR_STOP on

CREATE TEMP TABLE indexing_demo_orders (
    order_id bigint PRIMARY KEY,
    customer_id integer NOT NULL,
    status text NOT NULL,
    order_date date NOT NULL,
    total_cents integer NOT NULL
);

INSERT INTO indexing_demo_orders (
    order_id,
    customer_id,
    status,
    order_date,
    total_cents
)
SELECT
    g,
    (g % 5000)::integer,
    CASE WHEN g % 10 = 0 THEN 'open' ELSE 'closed' END,
    DATE '2025-01-01' + ((g % 650)::integer),
    1000 + (g % 100000)::integer
FROM generate_series(1, 200000) AS g;

CREATE INDEX idx_indexing_demo_open_orders
ON indexing_demo_orders(customer_id, order_date DESC)
INCLUDE (total_cents)
WHERE status = 'open';

ANALYZE indexing_demo_orders;

\echo ''
\echo 'Partial + covering index definition:'
SELECT pg_get_indexdef('idx_indexing_demo_open_orders'::regclass);

\echo ''
\echo 'Query that explicitly matches the partial-index predicate:'
EXPLAIN (COSTS OFF)
SELECT order_date, total_cents
FROM indexing_demo_orders
WHERE customer_id = 42
  AND status = 'open'
ORDER BY order_date DESC
LIMIT 20;

\echo ''
\echo 'Query without status=open cannot rely on the partial index:'
EXPLAIN (COSTS OFF)
SELECT order_date, total_cents
FROM indexing_demo_orders
WHERE customer_id = 42
ORDER BY order_date DESC
LIMIT 20;

CREATE TEMP TABLE indexing_demo_users (
    user_id bigint PRIMARY KEY,
    email text NOT NULL,
    display_name text NOT NULL
);

INSERT INTO indexing_demo_users(user_id, email, display_name)
SELECT
    g,
    'user-' || g || '@example.com',
    'User ' || g
FROM generate_series(1, 100000) AS g;

CREATE INDEX idx_indexing_demo_users_lower_email
ON indexing_demo_users(lower(email));

ANALYZE indexing_demo_users;

\echo ''
\echo 'Expression index definition:'
SELECT pg_get_indexdef(
    'idx_indexing_demo_users_lower_email'::regclass
);

\echo ''
\echo 'Case-normalized lookup using the indexed expression:'
EXPLAIN (COSTS OFF)
SELECT user_id, display_name
FROM indexing_demo_users
WHERE lower(email) = lower('USER-4242@EXAMPLE.COM');
