"""Airflow DAG: daily financial transaction ETL pipeline."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def _extract(**context):
    from pipeline.extract import extract
    df = extract()
    context["ti"].xcom_push(key="raw_count", value=len(df))
    df.to_parquet("/tmp/raw_transactions.parquet", index=False)


def _transform(**context):
    import pandas as pd
    from pipeline.transform import transform
    df = pd.read_parquet("/tmp/raw_transactions.parquet")
    cleaned = transform(df)
    cleaned.to_parquet("/tmp/transformed_transactions.parquet", index=False)
    context["ti"].xcom_push(key="transformed_count", value=len(cleaned))


def _load(**context):
    import pandas as pd
    from pipeline.load import create_schema, load, _get_engine
    engine = _get_engine()
    create_schema(engine)
    df = pd.read_parquet("/tmp/transformed_transactions.parquet")
    rows = load(df, engine=engine, if_exists="append")
    context["ti"].xcom_push(key="loaded_count", value=rows)


def _refresh_views(**context):
    from sqlalchemy import create_engine, text
    from pipeline.config import DATABASE_URL
    engine = create_engine(DATABASE_URL)
    with open("sql/analytical_views.sql") as f:
        sql = f.read()
    with engine.begin() as conn:
        conn.execute(text(sql))


def _anomaly_alert(**context):
    from analytics.anomalies import anomaly_summary
    summary = anomaly_summary()
    print(f"[ANOMALY REPORT] {summary}")
    # Extend here: send to Slack / PagerDuty / email


with DAG(
    dag_id="financial_etl_pipeline",
    default_args=DEFAULT_ARGS,
    description="Daily ETL: ingest synthetic transactions → PostgreSQL → analytics views",
    schedule_interval="0 2 * * *",   # 02:00 UTC daily
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["fintech", "etl", "analytics"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract_transactions",
        python_callable=_extract,
    )

    transform_task = PythonOperator(
        task_id="transform_transactions",
        python_callable=_transform,
    )

    load_task = PythonOperator(
        task_id="load_to_postgres",
        python_callable=_load,
    )

    refresh_views_task = PythonOperator(
        task_id="refresh_analytical_views",
        python_callable=_refresh_views,
    )

    anomaly_task = PythonOperator(
        task_id="anomaly_detection_alert",
        python_callable=_anomaly_alert,
    )

    extract_task >> transform_task >> load_task >> refresh_views_task >> anomaly_task
