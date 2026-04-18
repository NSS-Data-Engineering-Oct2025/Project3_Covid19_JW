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


class PipelineError(Exception):
    """Raised when a pipeline step fails."""


def _check_prerequisites() -> None:
    """Fail fast if required environment variables are missing."""
    if not (census.api_key or "").strip():
        raise PipelineError("CENSUS_API_KEY is not set — cannot retrieve population data.")
    if not (snowflake.account or "").strip():
        raise PipelineError("SNOWFLAKE_ACCOUNT is not set — cannot connect to Snowflake.")
    logger.info("Prerequisites check passed.")


def run_ingestion() -> dict:
    logger.info("=" * 50)
    logger.info("STEP 1 — Data Ingestion")
    logger.info("=" * 50)

    results = {}

    logger.info("Ingesting CDC COVID cases...")
    results["covid_cases"] = ingest_cases(max_pages=None)

    logger.info("Ingesting CDC vaccinations...")
    results["vaccinations"] = ingest_vaccinations(max_pages=None)

    logger.info("Ingesting Census population...")
    results["population"] = ingest_population()

    return results


def run_dbt(command: str) -> None:
    result = subprocess.run(
        ["uv", "run", "dbt", *command.split()],
        cwd=DBT_DIR,
    )
    if result.returncode != 0:
        raise PipelineError(f"dbt {command} failed with exit code {result.returncode}")


def run_transformations() -> None:
    logger.info("=" * 50)
    logger.info("STEP 2 — dbt Transformations")
    logger.info("=" * 50)

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
        run_dbt(command)


def print_summary(ingestion_results: dict) -> None:
    logger.info("=" * 50)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 50)
    logger.info(f"  CDC Cases loaded:        {ingestion_results.get('covid_cases', 0):,} rows")
    logger.info(f"  Vaccinations loaded:     {ingestion_results.get('vaccinations', 0):,} rows")
    logger.info(f"  Population loaded:       {ingestion_results.get('population', 0):,} rows")
    logger.info("  dbt transformations:     PASS")
    logger.info("=" * 50)


def main():
    logger.info("Starting COVID-19 pipeline")
    try:
        _check_prerequisites()
        ingestion_results = run_ingestion()
        run_transformations()
        print_summary(ingestion_results)
        logger.success("Pipeline completed successfully. Data is ready in Snowflake MARTS.")
    except PipelineError as exc:
        logger.error(f"Pipeline failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
