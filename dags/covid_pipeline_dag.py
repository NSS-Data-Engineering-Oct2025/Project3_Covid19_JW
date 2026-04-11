"""
Airflow DAG: covid_pipeline
Orchestrates: ingestion → dbt staging → dbt intermediate → dbt marts → dbt test → quality report
Schedule: weekly (COVID data updates are no longer daily)
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Path where dbt project lives — adjust if you move the repo
DBT_PROJECT_DIR = "/path/to/Project3_Covid19_JW/covid_19"
DBT_PROFILES_DIR = "~/.dbt"

default_args = {
    "owner": "wilmer",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

with DAG(
    dag_id="covid_pipeline",
    description="COVID-19 ingestion → dbt → Snowflake pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="@weekly",
    catchup=False,
    tags=["covid", "cdc", "census", "dbt"],
) as dag:

    # ── Ingestion tasks ──────────────────────────────────────────────────────

    import os
    DEMO_MODE = os.environ.get("AIRFLOW_DEMO_MODE", "false").lower() == "true"
    MAX_PAGES = 2 if DEMO_MODE else None  # 2 pages (~100k rows) for demo, full load otherwise

    def run_ingest_cases():
        from src.ingest_covid_cases import ingest
        ingest(max_pages=MAX_PAGES)

    def run_ingest_vaccinations():
        from src.ingest_vaccinations import ingest
        ingest(max_pages=MAX_PAGES)

    def run_ingest_population():
        from src.ingest_population import ingest
        ingest()

    ingest_cases = PythonOperator(
        task_id="ingest_covid_cases",
        python_callable=run_ingest_cases,
    )

    ingest_vaccinations = PythonOperator(
        task_id="ingest_vaccinations",
        python_callable=run_ingest_vaccinations,
    )

    ingest_population = PythonOperator(
        task_id="ingest_population",
        python_callable=run_ingest_population,
    )

    # ── dbt tasks ────────────────────────────────────────────────────────────

    dbt_cmd = (
        f"dbt {{command}} "
        f"--project-dir {DBT_PROJECT_DIR} "
        f"--profiles-dir {DBT_PROFILES_DIR}"
    )

    dbt_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command=dbt_cmd.format(command="run --select staging"),
    )

    dbt_intermediate = BashOperator(
        task_id="dbt_run_intermediate",
        bash_command=dbt_cmd.format(command="run --select intermediate"),
    )

    dbt_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command=dbt_cmd.format(command="run --select marts"),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=dbt_cmd.format(command="test"),
    )

    # ── Quality report ───────────────────────────────────────────────────────

    def quality_report(**context):
        """Log pipeline run summary to Airflow logs."""
        from loguru import logger
        run_date = context["ds"]
        logger.info(f"Pipeline run complete for {run_date}")
        logger.info("Check mart_data_freshness in Snowflake for source-level freshness.")

    quality_report_task = PythonOperator(
        task_id="quality_report",
        python_callable=quality_report,
        provide_context=True,
    )

    # ── DAG dependencies ─────────────────────────────────────────────────────

    [ingest_cases, ingest_vaccinations, ingest_population] >> dbt_staging
    dbt_staging >> dbt_intermediate >> dbt_marts >> dbt_test >> quality_report_task
