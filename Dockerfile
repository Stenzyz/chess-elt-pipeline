FROM apache/airflow:3.3.0

RUN pip install --no-cache-dir httpx "psycopg[binary]" tenacity python-dotenv dbt-postgres==1.9.9