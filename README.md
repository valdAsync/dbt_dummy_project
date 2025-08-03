# dbt + DuckDB Dummy Data Warehouse

A plug-and-play local analytics stack using:

- **[dbt Core](https://docs.getdbt.com/)** for transformations
- **[DuckDB](https://duckdb.org/)** as a fast, serverless data warehouse
- **[Polars](https://pola.rs/)** for blazing-fast data generation
- **[uv](https://github.com/astral-sh/uv)** for ultra-fast Python environment setup
- **[Airflow](https://airflow.apache.org/)** for workflow orchestration
- **[MinIO](https://min.io/)** for S3-compatible object storage

> No cloud. No external dependencies. Learn the modern data stack locally.

---

## Two Ways to Run This Project

This project can be run in two ways:

1. **Local dbt Setup:** A simple, lightweight setup for running dbt transformations with DuckDB. This does not require Docker.
2. **Full Data Stack with Docker:** A complete, containerized data stack with Airflow and MinIO for orchestration and object storage. This requires Docker.

---

## Option 1: Local dbt Setup (No Docker)

This setup is ideal for quickly running and testing dbt models without the overhead of Docker.

### 1. Clone the Project

```bash
git clone https://github.com/valdAsync/dbt_dummy_project.git
cd dbt_dummy_project
```

### 2. Sync dependencies using UV package manager

1. Install UV packager manager - <https://docs.astral.sh/uv/getting-started/installation/>
2. Run command - `uv sync`

This installs all the necessary Python packages defined in `pyproject.toml`.

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

- `raw` and `analytics` schemas
- `raw.customers`: A dimension table with 10,000 unique customers.
- `raw.products`: A dimension table with 1,000 unique products.
- `raw.locations`: A dimension table with 100 unique store locations.
- `raw.purchases`: A fact table with 1 million purchase events, linked to customers, products, and locations.
- `raw.page_views`: A fact table with 5 million page view events, linked to customers.
- All tables include an `updated_on` timestamp for incremental modeling.

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

### 6. Run dbt Models

```bash
dbt debug        # Check connection
dbt parse        # Validate project structure
dbt run          # Run all models
dbt docs generate && dbt docs serve  # Open docs in browser
```

---

## Option 2: Full Data Stack with Docker (Airflow + MinIO)

This setup provides a complete, containerized data stack with Airflow for orchestration and MinIO for S3-compatible object storage.

### 1. Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 2. Build and Start the Data Stack

Run the following command to build the custom Airflow image and start all services in detached mode:

```bash
docker-compose up -d --build
```

The first build will take several minutes as it needs to download the base Airflow image and install all Python dependencies. Subsequent builds will be much faster.

This command will:

- Build a custom Docker image based on the `Dockerfile`, which starts from the official Airflow image and installs all project dependencies from `pyproject.toml` using `uv`.
- Start all services defined in `docker-compose.yaml`:
  - **PostgreSQL:** The metadata database for Airflow.
  - **MinIO:** An S3-compatible object storage service.
  - **Airflow:** The webserver, scheduler, and triggerer services.
  - A **minio-setup** service that automatically creates a `raw` bucket in MinIO upon startup.
  - An **airflow-init** service that initializes the Airflow database and creates a default user.

### 3. Access the Services

- **Airflow Web UI:**
  - **URL:** `http://localhost:8080`
  - **Username:** `admin`
  - **Password:** `admin`
- **MinIO Console:**
  - **URL:** `http://localhost:9001`
  - **Username:** `minioadmin`
  - **Password:** `minioadmin`

### 4. Example ETL DAG

This project includes an example DAG named `etl_load_dummy_data_to_minio` that demonstrates a simple ETL process:

1. **Generate Data:** It calls a Python function to generate several Polars DataFrames.
2. **Upload to MinIO:** It converts each DataFrame to a CSV file in memory and uploads it to the `raw` bucket in MinIO.

To run it, go to the Airflow UI, find the DAG, and trigger it manually. You will see files like `customers_20240803.csv` appear in your MinIO `raw` bucket.

### 5. Stop the Data Stack

To stop all the services, run:

```bash
docker-compose down
```
