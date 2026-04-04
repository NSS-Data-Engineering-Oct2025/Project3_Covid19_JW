"""
COVID-19 Pipeline — Manual Orchestrator
Runs the full pipeline in sequence: ingest → dbt run → dbt test
Usage: uv run python main.py
"""

import subprocess
import sys
from pathlib import Path
from loguru import logger

ROOT_DIR = Path(__file__).parent
DBT_DIR = ROOT_DIR / "dbt_project"


def run_ingestion() -> dict:
    logger.info("=" * 50)
    logger.info("STEP 1 — Data Ingestion")
    logger.info("=" * 50)

    from src.ingest_covid_cases import ingest as ingest_cases
    from src.ingest_vaccinations import ingest as ingest_vaccinations
    from src.ingest_population import ingest as ingest_population

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

    steps = [
        ("run --select staging",      "Staging models"),
        ("run --select intermediate", "Intermediate models"),
        ("run --select marts",        "Mart models"),
    ]

    for command, label in steps:
        logger.info(f"Running {label}...")
        if not run_dbt(command):
            logger.error(f"{label} failed — stopping pipeline")
            return False

    return True


def run_tests() -> bool:
    logger.info("=" * 50)
    logger.info("STEP 3 — dbt Tests")
    logger.info("=" * 50)
    return run_dbt("test")


def print_summary(ingestion_results: dict, dbt_success: bool, tests_success: bool) -> None:
    logger.info("=" * 50)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 50)
    logger.info(f"  CDC Cases loaded:        {ingestion_results.get('covid_cases', 0):,} rows")
    logger.info(f"  Vaccinations loaded:     {ingestion_results.get('vaccinations', 0):,} rows")
    logger.info(f"  Population loaded:       {ingestion_results.get('population', 0):,} rows")
    logger.info(f"  dbt transformations:     {'PASS' if dbt_success else 'FAIL'}")
    logger.info(f"  dbt tests:               {'PASS' if tests_success else 'WARN/FAIL'}")
    logger.info("=" * 50)

    if dbt_success:
        logger.success("Pipeline completed successfully. Data is ready in Snowflake MARTS.")
    else:
        logger.error("Pipeline completed with errors. Check logs above.")


def main():
    logger.info("Starting COVID-19 pipeline")

    ingestion_results = run_ingestion()
    dbt_success = run_transformations()

    if not dbt_success:
        logger.error("dbt transformations failed — skipping tests")
        print_summary(ingestion_results, dbt_success=False, tests_success=False)
        sys.exit(1)

    tests_success = run_tests()
    print_summary(ingestion_results, dbt_success=True, tests_success=tests_success)


if __name__ == "__main__":
    main()
