"""
COVID-19 Pipeline — Manual Orchestrator
Runs the full pipeline in sequence: ingest → dbt run → dbt test
Usage: uv run python main.py
"""

import subprocess
import sys
from pathlib import Path

from loguru import logger

from src.config import census, snowflake
from src.ingest_covid_cases import ingest as ingest_cases
from src.ingest_vaccinations import ingest as ingest_vaccinations
from src.ingest_population import ingest as ingest_population

ROOT_DIR = Path(__file__).parent
DBT_DIR = ROOT_DIR / "covid_19"


def _check_prerequisites() -> None:
    """Fail fast if required environment variables are missing."""
    if not (census.api_key or "").strip():
        logger.error("CENSUS_API_KEY is not set — cannot retrieve population data.")
        sys.exit(1)
    if not (snowflake.account or "").strip():
        logger.error("SNOWFLAKE_ACCOUNT is not set — cannot connect to Snowflake.")
        sys.exit(1)
    logger.info("Prerequisites check passed.")


def run_ingestion() -> dict:
    logger.info("=" * 50)
    logger.info("STEP 1 — Data Ingestion")
    logger.info("=" * 50)

    results = {}

    logger.info("Ingesting CDC COVID cases...")
    results["covid_cases"] = ingest_cases(max_pages=None)  # full load

    logger.info("Ingesting CDC vaccinations...")
    results["vaccinations"] = ingest_vaccinations(max_pages=None)  # full load

    logger.info("Ingesting Census population...")
    results["population"] = ingest_population()

    return results


def run_dbt(command: str) -> bool:
    result = subprocess.run(
        ["uv", "run", "dbt", *command.split()],
        cwd=DBT_DIR,
        capture_output=False,
    )
    return result.returncode == 0


def run_transformations() -> bool:
    logger.info("=" * 50)
    logger.info("STEP 2 — dbt Transformations")
    logger.info("=" * 50)

    # Tests run after each layer — catches issues earlier in the pipeline
    steps = [
        ("run --select staging",        "Staging models"),
        ("test --select staging+",      "Staging tests"),
        ("run --select intermediate",   "Intermediate models"),
        ("test --select intermediate+", "Intermediate tests"),
        ("run --select marts",          "Mart models"),
        ("test --select marts+",        "Mart tests"),
    ]

    for command, label in steps:
        logger.info(f"Running {label}...")
        if not run_dbt(command):
            logger.error(f"{label} failed — stopping pipeline")
            return False

    return True


def print_summary(ingestion_results: dict, dbt_success: bool) -> None:
    logger.info("=" * 50)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 50)
    logger.info(f"  CDC Cases loaded:        {ingestion_results.get('covid_cases', 0):,} rows")
    logger.info(f"  Vaccinations loaded:     {ingestion_results.get('vaccinations', 0):,} rows")
    logger.info(f"  Population loaded:       {ingestion_results.get('population', 0):,} rows")
    logger.info(f"  dbt transformations:     {'PASS' if dbt_success else 'FAIL'}")
    logger.info("=" * 50)

    if dbt_success:
        logger.success("Pipeline completed successfully. Data is ready in Snowflake MARTS.")
    else:
        logger.error("Pipeline completed with errors. Check logs above.")


def main():
    logger.info("Starting COVID-19 pipeline")
    _check_prerequisites()

    ingestion_results = run_ingestion()
    dbt_success = run_transformations()

    print_summary(ingestion_results, dbt_success)

    if not dbt_success:
        sys.exit(1)


if __name__ == "__main__":
    main()
