import sys
import shlex
from pathlib import Path
import subprocess
from loguru import logger
from src.config import census
from src.ingest_covid_cases import ingest as ingest_covid_cases
from src.ingest_population import ingest as ingest_population
from src.ingest_vaccinations import ingest as ingest_vaccinations


ROOT_DIR = Path(__file__).parent
DBT_DIR = ROOT_DIR / "covid_19"


def ingestion(name: str, fn):
    logger.info(f"Ingest: {name} Started")
    rows = fn()
    logger.info(f"Ingest Summary — {name}: {rows} rows")
    return rows


def dbt(command: str) -> bool:
    result = subprocess.run(
        ["uv", "run", "dbt", *shlex.split(command)()],
        cwd=DBT_DIR,
        capture_output=False,
    )
    return result.returncode == 0


def transformations() -> bool:

    logger.info("Dbt Transformations Started")

    layers = [
        ("run --select staging",      "Staging models"),
        ("test --select staging+",     "Staging tests"),
        ("run --select intermediate", "Intermediate models"),
        ("test --select intermediate+",     "Intermediate tests"),
        ("run --select marts", "Mart models"),
        ("test --select marts+", "Mart tests"),
    ]

    for command, label in layers:
        logger.info(f"Running {label}...")
        if not dbt(command):
            logger.error(f"{label} failed — stopping pipeline")
            return False

    logger.info("Dbt Transformations Completed Successfully")
    return True


def main() -> None:
    if not (census.api_key or "").strip():
        logger.error(
            "CENSUS_API_KEY is not set, can't retrieve population data.")
        sys.exit(1)

    ingestion("CDC COVID cases", ingest_covid_cases)

    ingestion("CDC Vaccinations", ingest_vaccinations)

    ingestion("US Census Population", ingest_population)

    logger.info("Ingestion pipeline finished successfully.")

    if not transformations():
        sys.exit(1)

    logger.info("Pipeline completed successfully")


if __name__ == "__main__":
    main()

# (cd covid_19)
# (dbt run)
# (uv run python main.py)
# to manually run pipeline in terminal
