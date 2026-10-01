"""Measure local PostgreSQL connection reuse and insert batching.

Prerequisites:
    cd scripts
    bash setup/start_postgres.sh
    cd ..

Run:
    python scripts/performance/postgres_pool_and_batch_demo.py

Optional:
    export DATABASE_URL='postgresql://demo:secret@127.0.0.1:5432/test'

The timings are local teaching measurements, not universal benchmark results.
"""
from __future__ import annotations

import os
import time

import psycopg2
from psycopg2 import pool
from psycopg2.extras import execute_values


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://demo:secret@127.0.0.1:5432/test",
)
ROW_COUNT = 5_000


def reset_table(connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS performance_batch_demo")
        cursor.execute(
            """
            CREATE TABLE performance_batch_demo (
                event_id bigint PRIMARY KEY,
                customer_id bigint NOT NULL,
                payload text NOT NULL
            )
            """
        )
    connection.commit()


def rows():
    return [
        (
            event_id,
            event_id % 1000,
            f"payload-{event_id}",
        )
        for event_id in range(1, ROW_COUNT + 1)
    ]


def measure_single_execute(connection) -> float:
    reset_table(connection)
    data = rows()

    started = time.perf_counter()
    with connection.cursor() as cursor:
        for row in data:
            cursor.execute(
                """
                INSERT INTO performance_batch_demo (
                    event_id,
                    customer_id,
                    payload
                )
                VALUES (%s, %s, %s)
                """,
                row,
            )
    connection.commit()
    return time.perf_counter() - started


def measure_execute_values(connection) -> float:
    reset_table(connection)
    data = rows()

    started = time.perf_counter()
    with connection.cursor() as cursor:
        execute_values(
            cursor,
            """
            INSERT INTO performance_batch_demo (
                event_id,
                customer_id,
                payload
            )
            VALUES %s
            """,
            data,
            page_size=500,
        )
    connection.commit()
    return time.perf_counter() - started


def measure_new_connections(repeats: int = 20) -> float:
    started = time.perf_counter()
    for _ in range(repeats):
        connection = psycopg2.connect(DATABASE_URL)
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        connection.close()
    return time.perf_counter() - started


def measure_pool_checkouts(
    connection_pool: pool.SimpleConnectionPool,
    repeats: int = 20,
) -> float:
    started = time.perf_counter()
    for _ in range(repeats):
        connection = connection_pool.getconn()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            # SELECT starts a transaction with psycopg2 defaults.
            # End it before returning the session to the pool.
            connection.rollback()
        finally:
            connection_pool.putconn(connection)
    return time.perf_counter() - started


def main() -> None:
    connection = psycopg2.connect(DATABASE_URL)
    try:
        single_time = measure_single_execute(connection)
        batch_time = measure_execute_values(connection)

        print(f"Rows inserted per run: {ROW_COUNT}")
        print(f"Single execute loop: {single_time:.6f} s")
        print(f"Batched execute_values: {batch_time:.6f} s")
        if batch_time > 0:
            print(
                "Local insert speed ratio "
                f"(single / batched): {single_time / batch_time:.2f}x"
            )
    finally:
        connection.close()

    new_connection_time = measure_new_connections()

    connection_pool = pool.SimpleConnectionPool(
        minconn=1,
        maxconn=4,
        dsn=DATABASE_URL,
    )
    try:
        pooled_time = measure_pool_checkouts(connection_pool)
    finally:
        connection_pool.closeall()

    print("\n20 SELECT 1 operations:")
    print(f"Open/close a new connection each time: {new_connection_time:.6f} s")
    print(f"Reuse pooled connections:             {pooled_time:.6f} s")
    if pooled_time > 0:
        print(
            "Local connection speed ratio "
            f"(new / pooled): {new_connection_time / pooled_time:.2f}x"
        )


if __name__ == "__main__":
    main()
