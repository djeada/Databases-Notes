"""Small local dimensional-model demo using DuckDB.

Run from the repository root:
    python -m pip install duckdb
    python scripts/big_data/warehouse_demo.py
"""

import duckdb


def main() -> None:
    con = duckdb.connect(":memory:")

    con.execute("""
        CREATE TABLE dim_date (
            date_key INTEGER PRIMARY KEY,
            calendar_date DATE NOT NULL,
            year INTEGER NOT NULL
        );

        CREATE TABLE dim_product (
            product_key INTEGER PRIMARY KEY,
            sku VARCHAR NOT NULL UNIQUE,
            category VARCHAR NOT NULL
        );

        CREATE TABLE fact_sales (
            order_id INTEGER NOT NULL,
            line_number INTEGER NOT NULL,
            date_key INTEGER NOT NULL,
            product_key INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
            PRIMARY KEY (order_id, line_number)
        );
    """)

    con.execute("""
        INSERT INTO dim_date VALUES
            (20260101, DATE '2026-01-01', 2026),
            (20260102, DATE '2026-01-02', 2026);

        INSERT INTO dim_product VALUES
            (1, 'BOOK-001', 'Books'),
            (2, 'GAME-001', 'Games');

        INSERT INTO fact_sales VALUES
            (1001, 1, 20260101, 1, 2, 15.00),
            (1001, 2, 20260101, 2, 3, 10.00),
            (1002, 1, 20260102, 1, 1, 20.00);
    """)

    query = """
        SELECT
            d.year,
            p.category,
            SUM(s.quantity * s.unit_price) AS revenue
        FROM fact_sales AS s
        JOIN dim_date AS d
          ON d.date_key = s.date_key
        JOIN dim_product AS p
          ON p.product_key = s.product_key
        GROUP BY d.year, p.category
        ORDER BY d.year, revenue DESC;
    """

    print("Revenue by year and category:")
    for year, category, revenue in con.execute(query).fetchall():
        print(f"{year}  {category:<8}  {revenue:.2f}")

    print("\nGrain check: one fact row = one order line")
    print("fact_sales rows:", con.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0])


if __name__ == "__main__":
    main()
