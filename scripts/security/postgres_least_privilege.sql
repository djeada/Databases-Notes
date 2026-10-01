\set ON_ERROR_STOP on

DROP SCHEMA IF EXISTS security_demo CASCADE;

DO $
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'security_demo_reader_login'
    ) THEN
        EXECUTE 'DROP OWNED BY security_demo_reader_login';
        EXECUTE 'DROP ROLE security_demo_reader_login';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'security_demo_writer_login'
    ) THEN
        EXECUTE 'DROP OWNED BY security_demo_writer_login';
        EXECUTE 'DROP ROLE security_demo_writer_login';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'security_demo_read'
    ) THEN
        EXECUTE 'DROP OWNED BY security_demo_read';
        EXECUTE 'DROP ROLE security_demo_read';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'security_demo_write'
    ) THEN
        EXECUTE 'DROP OWNED BY security_demo_write';
        EXECUTE 'DROP ROLE security_demo_write';
    END IF;
END;
$;

CREATE ROLE security_demo_read NOLOGIN;
CREATE ROLE security_demo_write NOLOGIN;

CREATE ROLE security_demo_reader_login
    LOGIN
    PASSWORD 'local-demo-only';

CREATE ROLE security_demo_writer_login
    LOGIN
    PASSWORD 'local-demo-only';

GRANT security_demo_read TO security_demo_reader_login;
GRANT security_demo_read, security_demo_write
TO security_demo_writer_login;

CREATE SCHEMA security_demo AUTHORIZATION demo;

CREATE TABLE security_demo.products (
    product_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku text UNIQUE NOT NULL,
    name text NOT NULL,
    price numeric(12, 2) NOT NULL CHECK (price >= 0)
);

INSERT INTO security_demo.products (sku, name, price)
VALUES
    ('DB-101', 'Database Systems', 49.90),
    ('SEC-201', 'Database Security', 39.00);

GRANT USAGE ON SCHEMA security_demo
TO security_demo_read, security_demo_write;

GRANT SELECT
ON ALL TABLES IN SCHEMA security_demo
TO security_demo_read;

GRANT INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA security_demo
TO security_demo_write;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA security_demo
TO security_demo_write;

ALTER DEFAULT PRIVILEGES FOR ROLE demo
IN SCHEMA security_demo
GRANT SELECT ON TABLES TO security_demo_read;

ALTER DEFAULT PRIVILEGES FOR ROLE demo
IN SCHEMA security_demo
GRANT INSERT, UPDATE, DELETE ON TABLES TO security_demo_write;

ALTER DEFAULT PRIVILEGES FOR ROLE demo
IN SCHEMA security_demo
GRANT USAGE, SELECT ON SEQUENCES TO security_demo_write;

\echo ''
\echo 'Reader can SELECT:'
SET ROLE security_demo_reader_login;
SELECT product_id, sku, name, price
FROM security_demo.products
ORDER BY product_id;
RESET ROLE;

\echo ''
\echo 'Writer can insert without owning the table:'
SET ROLE security_demo_writer_login;
INSERT INTO security_demo.products (sku, name, price)
VALUES ('OPS-301', 'Database Operations', 29.00);
RESET ROLE;

\echo ''
\echo 'Current role memberships:'
SELECT
    member_role.rolname AS member,
    granted_role.rolname AS granted_role
FROM pg_auth_members AS membership
JOIN pg_roles AS granted_role
  ON granted_role.oid = membership.roleid
JOIN pg_roles AS member_role
  ON member_role.oid = membership.member
WHERE member_role.rolname LIKE 'security_demo_%'
ORDER BY member, granted_role;

\echo ''
\echo 'Table privileges:'
SELECT
    grantee,
    privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'security_demo'
  AND table_name = 'products'
ORDER BY grantee, privilege_type;
