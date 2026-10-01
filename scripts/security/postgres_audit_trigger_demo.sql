\set ON_ERROR_STOP on

DROP SCHEMA IF EXISTS security_audit_demo CASCADE;
CREATE SCHEMA security_audit_demo;

CREATE TABLE security_audit_demo.customers (
    customer_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL,
    email text UNIQUE NOT NULL
);

CREATE TABLE security_audit_demo.customer_history (
    audit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    changed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    db_user text NOT NULL DEFAULT current_user,
    action text NOT NULL CHECK (action IN ('UPDATE', 'DELETE')),
    customer_id bigint NOT NULL,
    old_row jsonb,
    new_row jsonb
);

CREATE OR REPLACE FUNCTION security_audit_demo.audit_customer_change()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO security_audit_demo.customer_history (
            action,
            customer_id,
            old_row,
            new_row
        )
        VALUES (
            TG_OP,
            OLD.customer_id,
            to_jsonb(OLD),
            to_jsonb(NEW)
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO security_audit_demo.customer_history (
            action,
            customer_id,
            old_row,
            new_row
        )
        VALUES (
            TG_OP,
            OLD.customer_id,
            to_jsonb(OLD),
            NULL
        );
        RETURN OLD;
    END IF;

    RAISE EXCEPTION 'Unexpected trigger operation: %', TG_OP;
END;
$$;

CREATE TRIGGER customers_audit
AFTER UPDATE OR DELETE
ON security_audit_demo.customers
FOR EACH ROW
EXECUTE FUNCTION security_audit_demo.audit_customer_change();

INSERT INTO security_audit_demo.customers (name, email)
VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com');

UPDATE security_audit_demo.customers
SET email = 'alice.updated@example.com'
WHERE name = 'Alice';

DELETE FROM security_audit_demo.customers
WHERE name = 'Bob';

\echo ''
\echo 'Current rows:'
TABLE security_audit_demo.customers;

\echo ''
\echo 'Audit history:'
SELECT
    audit_id,
    changed_at,
    db_user,
    action,
    customer_id,
    old_row,
    new_row
FROM security_audit_demo.customer_history
ORDER BY audit_id;
