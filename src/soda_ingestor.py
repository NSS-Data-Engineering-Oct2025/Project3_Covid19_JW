"""
Shared SODA API pagination logic for CDC endpoints.
Both ingest_covid_cases.py and ingest_vaccinations.py use this.
"""

import time
import requests
import pandas as pd
from loguru import logger
from src.config import cdc
from src.load_to_snowflake import load_dataframe


def fetch_page(endpoint: str, offset: int, limit: int, order_by: str) -> list[dict]:
    """Fetch one page from a SODA API endpoint with exponential backoff retry."""
    params = {
        "$limit": limit,
        "$offset": offset,
        "$order": order_by,
    }
    for attempt in range(1, cdc.max_retries + 1):
        try:
            resp = requests.get(endpoint, params=params, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.warning(f"Attempt {attempt}/{cdc.max_retries} failed: {exc}")
            if attempt < cdc.max_retries:
                time.sleep(cdc.backoff_seconds ** attempt)  # exponential backoff
    raise RuntimeError(f"All {cdc.max_retries} attempts failed for {endpoint}")


def paginate_and_load(
    endpoint: str,
    target_table: str,
    target_schema: str,
    order_by: str,
    source_name: str,
    max_pages: int | None = None,
) -> int:
    """
    Paginate through a SODA API and load all records into Snowflake.

    Parameters
    ----------
    endpoint     : SODA API URL
    target_table : Snowflake table name
    target_schema: Snowflake schema name
    order_by     : SODA $order parameter (e.g. 'case_month DESC')
    source_name  : Human-readable name for logging
    max_pages    : Page cap for smoke tests (None = load all)

    Returns
    -------
    int : Total rows loaded
    """
    logger.info(f"Starting {source_name} ingestion")
    total_rows = 0
    offset = 0
    page = 0

    while True:  #while true is an antipattern, should have an exit condition
        if max_pages is not None and page >= max_pages:
            logger.info(f"Reached max_pages={max_pages}, stopping early")
            break

        logger.info(f"Fetching page {page + 1} (offset={offset})")
        records = fetch_page(endpoint, offset, cdc.page_size, order_by)

        if not records:
            logger.info("No more records returned — ingestion complete")
            break

        df = pd.DataFrame(records)
        df.columns = [c.upper() for c in df.columns]

        rows = load_dataframe(df, table=target_table, schema=target_schema, if_exists="append")
        total_rows += rows
        offset += cdc.page_size
        page += 1

    logger.info(f"{source_name} ingestion finished — {total_rows} total rows loaded")
    return total_rows
