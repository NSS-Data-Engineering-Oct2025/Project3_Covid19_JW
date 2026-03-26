"""
CDC COVID-19 Cases with Geography ingestion.
Endpoint: https://data.cdc.gov/resource/n8mc-b4w4.json  (SODA, no auth)
Target:   RAW.RAW_COVID_CASES
"""

import time
import requests
import pandas as pd
from loguru import logger
from src.config import cdc
from src.load_to_snowflake import load_dataframe

TARGET_TABLE = "RAW_COVID_CASES"
TARGET_SCHEMA = "RAW"

# Keep only the last N years to avoid loading the full dataset on every run
DATE_FILTER_YEARS = 3


def fetch_page(offset: int, limit: int) -> list[dict]:
    params = {
        "$limit": limit,
        "$offset": offset,
        "$order": "case_month DESC",
    }
    for attempt in range(1, cdc.max_retries + 1):
        try:
            resp = requests.get(cdc.cases_endpoint, params=params, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.warning(f"Attempt {attempt}/{cdc.max_retries} failed: {exc}")
            if attempt < cdc.max_retries:
                time.sleep(cdc.backoff_seconds * attempt)
    raise RuntimeError(f"All {cdc.max_retries} attempts failed for cases endpoint")


def ingest(max_pages: int | None = None) -> int:
    """
    Paginate through the CDC cases API and load all records into Snowflake.

    Parameters
    ----------
    max_pages : cap for testing (None = load all)

    Returns
    -------
    int : Total rows loaded
    """
    logger.info("Starting CDC COVID cases ingestion")
    total_rows = 0
    offset = 0
    page = 0

    while True:
        if max_pages is not None and page >= max_pages:
            logger.info(f"Reached max_pages={max_pages}, stopping early")
            break

        logger.info(f"Fetching page {page + 1} (offset={offset})")
        records = fetch_page(offset, cdc.page_size)

        if not records:
            logger.info("No more records returned — ingestion complete")
            break

        df = pd.DataFrame(records)
        df.columns = [c.upper() for c in df.columns]

        rows = load_dataframe(df, table=TARGET_TABLE, schema=TARGET_SCHEMA, if_exists="append")
        total_rows += rows
        offset += cdc.page_size
        page += 1

    logger.info(f"CDC cases ingestion finished — {total_rows} total rows loaded")
    return total_rows


if __name__ == "__main__":
    ingest(max_pages=2)  # smoke test: 2 pages = 100k rows
