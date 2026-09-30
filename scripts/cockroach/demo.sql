CREATE DATABASE IF NOT EXISTS notes;
SET DATABASE = notes;

DROP TABLE IF EXISTS accounts;

CREATE TABLE accounts (
    id INT PRIMARY KEY,
    owner STRING UNIQUE NOT NULL,
    balance DECIMAL(12, 2) NOT NULL CHECK (balance >= 0)
);

INSERT INTO accounts (id, owner, balance) VALUES
    (1, 'Alice', 1000.00),
    (2, 'Bob', 500.00);

BEGIN;

UPDATE accounts
SET balance = balance - 125.00
WHERE id = 1;

UPDATE accounts
SET balance = balance + 125.00
WHERE id = 2;

COMMIT;

SELECT *
FROM accounts
ORDER BY id;
