from datetime import date

import duckdb
import numpy as np
import polars as pl

# random seed for reproducibility
np.random.seed(39)


# Generate small dimensions table
num_customers = 10_000
dim_customers = pl.DataFrame(
    {
        "customer_id": np.arange(1, num_customers + 1),
        "first_name": np.random.choice(
            ["Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace"],
            size=num_customers,
        ),
        "last_name": np.random.choice(
            ["Smith", "Johnson", "Williams", "Brown", "Jones"], size=num_customers
        ),
        "signup_date": np.random.choice(
            pl.date_range(
                date(2024, 1, 1), date(2024, 12, 31), "1d", eager=True
            ).to_numpy(),
            size=num_customers,
        ),
        "email_opt_in": np.random.choice([True, False], size=num_customers),
    }
)

# Generate big fact table
num_purchases = 10_000_000
fact_purchases = pl.DataFrame(
    {
        "customer_id": np.random.randint(1, num_customers + 1, size=num_purchases),
        "purchase_amount": np.round(
            np.random.exponential(scale=100.0, size=num_purchases), 2
        ),
        "purchase_date": np.random.choice(
            pl.date_range(
                date(2024, 1, 1), date(2024, 12, 31), "1d", eager=True
            ).to_numpy(),
            size=num_purchases,
        ),
        "product_category": np.random.choice(
            ["Books", "Electronics", "Clothing", "Home", "Toys"], size=num_purchases
        ),
    }
)

con = duckdb.connect("dummy_dwh.duckdb")
con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
con.execute("CREATE SCHEMA IF NOT EXISTS analytics;")

con.register("temp_dim", dim_customers)
con.register("temp_fact", fact_purchases)

# create raw.customers
con.execute(
    """
    CREATE TABLE IF NOT EXISTS raw.customers AS 
    SELECT *, current_timestamp::timestamp AS updated_on
    FROM temp_dim
    LIMIT 0
    """
)
con.execute(
    """
    INSERT INTO raw.customers 
    SELECT *, current_timestamp::timestamp AS updated_on
    FROM temp_dim
    """
)

# create raw.purchases
con.execute(
    """
    CREATE TABLE IF NOT EXISTS raw.purchases AS 
    SELECT *, current_timestamp::timestamp AS updated_on 
    FROM temp_fact
    LIMIT 0
    """
)
con.execute(
    """
    INSERT INTO raw.purchases 
    SELECT *, current_timestamp::timestamp AS updated_on 
    FROM temp_fact
    """
)

print("Customers:", con.execute("SELECT COUNT(*) FROM raw.customers;").fetchall()[0])
print("Purchases:", con.execute("SELECT COUNT(*) FROM raw.purchases;").fetchall()[0])

con.close()
