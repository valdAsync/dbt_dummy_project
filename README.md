# dbt + DuckDB Dummy Data Warehouse

A plug-and-play local analytics stack using:

- **[dbt Core](https://docs.getdbt.com/)** for transformations  
- **[DuckDB](https://duckdb.org/)** as a fast, serverless data warehouse  
- **[Polars](https://pola.rs/)** for blazing-fast data generation  
- **[uv](https://github.com/astral-sh/uv)** for ultra-fast Python environment setup  

> No cloud. No external dependencies. Learn the modern data stack locally.

---

## Quick Start

### 1. Clone the Project

```bash
git clone https://github.com/valdAsync/dbt_dummy_project.git
cd dbt_dummy_project
```

### 2. Sync dependencies using UV package manager

1. Install UV packager manager - <https://docs.astral.sh/uv/getting-started/installation/>
2. Run command - `uv sync`

This installs:

- dbt-core
- dbt-duckdb
- duckdb
- polars
- numpy
- pyarrow

### 3. Activate Python virtual environment

```bash
source .venv/bin/activate        # macOS/Linux
# OR
.venv\Scripts\activate           # Windows
```

### 4. Generate Dummy Data

Run the script to generate a local DuckDB database (`dummy_dwh.duckdb`) with synthetic tables:

```bash
python generate_dummy_data.py
```

This script creates:

- raw and analytics schemas
- raw.customers table — 10,000 rows of customer data
- raw.purchases table — 10M rows of purchase events
- Both tables include an updated_on timestamp

### 5. Update your profiles.yml file

Your `profiles.yml` should look like this:

```yaml
dbt_dummy_project:
  outputs:
    dev:
      type: duckdb
      path: dummy_dwh.duckdb
      threads: 1

    prod:
      type: duckdb
      path: dummy_dwh.duckdb
      threads: 4
  target: dev
```

### 5. Run dbt Models

```bash
dbt debug        # Check connection
dbt parse        # Validate project structure
dbt run          # Run all models
dbt docs generate && dbt docs serve  # Open docs in browser
```
