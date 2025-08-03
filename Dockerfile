FROM apache/airflow:2.8.4-python3.10

COPY --chown=airflow:airflow pyproject.toml uv.lock ./

RUN pip install --user --no-cache-dir uv

ENV PATH="/home/airflow/.local/bin:${PATH}"

RUN uv pip compile pyproject.toml --output-file requirements.txt

RUN pip install --user --no-cache-dir -r requirements.txt
