from datetime import date, datetime, timedelta

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

# Generate product dimension
num_products = 1_000
dim_products = pl.DataFrame(
    {
        "product_id": np.arange(1, num_products + 1),
        "product_name": [f"Product {i}" for i in range(1, num_products + 1)],
        "product_category": np.random.choice(
            ["Books", "Electronics", "Clothing", "Home", "Toys", "Sports", "Garden"],
            size=num_products,
        ),
        "brand": np.random.choice(
            ["BrandA", "BrandB", "BrandC", "BrandD"], size=num_products
        ),
        "price": np.round(np.random.uniform(5.0, 500.0, size=num_products), 2),
    }
)

# Generate location dimension
num_locations = 100
dim_locations = pl.DataFrame(
    {
        "location_id": np.arange(1, num_locations + 1),
        "city": [f"City {i}" for i in range(1, num_locations + 1)],
        "country": np.random.choice(
            ["USA", "Canada", "UK", "Germany", "France"], size=num_locations
        ),
    }
)


# Generate big fact table for purchases
num_purchases = 1_000_000
fact_purchases = pl.DataFrame(
    {
        "purchase_id": np.arange(1, num_purchases + 1),
        "customer_id": np.random.randint(1, num_customers + 1, size=num_purchases),
        "product_id": np.random.randint(1, num_products + 1, size=num_purchases),
        "location_id": np.random.randint(1, num_locations + 1, size=num_purchases),
        "purchase_amount": np.round(
            np.random.exponential(scale=100.0, size=num_purchases), 2
        ),
        "purchase_date": np.random.choice(
            pl.date_range(
                date(2024, 1, 1), date(2024, 12, 31), "1d", eager=True
            ).to_numpy(),
            size=num_purchases,
        ),
    }
)

# Generate another big fact table for page views
num_page_views = 5_000_000
fact_page_views = pl.DataFrame(
    {
        "view_id": np.arange(1, num_page_views + 1),
        "customer_id": np.random.randint(1, num_customers + 1, size=num_page_views),
        "page_name": np.random.choice(
            ["home", "product", "checkout", "search", "profile"], size=num_page_views
        ),
        "view_timestamp": [
            datetime(2024, 1, 1) + timedelta(seconds=int(s))
            for s in np.random.randint(0, 365 * 24 * 60 * 60, size=num_page_views)
        ],
    }
)


con = duckdb.connect("dummy_dwh.duckdb")
con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
con.execute("CREATE SCHEMA IF NOT EXISTS analytics;")

con.register("temp_dim_customers", dim_customers)
con.register("temp_dim_products", dim_products)
con.register("temp_dim_locations", dim_locations)
con.register("temp_fact_purchases", fact_purchases)
con.register("temp_fact_page_views", fact_page_views)

# Create and load tables
tables = {
    "customers": "temp_dim_customers",
    "products": "temp_dim_products",
    "locations": "temp_dim_locations",
    "purchases": "temp_fact_purchases",
    "page_views": "temp_fact_page_views",
}

for table_name, temp_df_name in tables.items():
    con.execute(f"DROP TABLE IF EXISTS raw.{table_name};")
    con.execute(
        f"""
        CREATE TABLE raw.{table_name} AS
        SELECT *, current_timestamp::timestamp AS updated_on
        FROM {temp_df_name}
        """
    )

for table_name in tables:
    count = con.execute(f"SELECT COUNT(*) FROM raw.{table_name};").fetchall()[0][0]
    print(f"{table_name.capitalize()}: {count}")

con.close()
