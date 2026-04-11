"""
US Census Population Estimates (County-level) ingestion.
Endpoint: https://api.census.gov/data/2023/pep/charv
Target:   RAW.RAW_POPULATION

Requires CENSUS_API_KEY in .env  (free at https://api.census.gov/data/key_signup.html)
"""

import time
import requests
import pandas as pd
from loguru import logger
from src.config import census, cdc
from src.load_to_snowflake import load_dataframe

TARGET_TABLE = "RAW_POPULATION"
TARGET_SCHEMA = "RAW"

VARIABLES = "POP,NAME"
GEOGRAPHY = "county:*"


def fetch_population() -> pd.DataFrame:
    params = {
        "get": VARIABLES,
        "for": GEOGRAPHY,
        "key": census.api_key,
    }
    for attempt in range(1, cdc.max_retries + 1):
        try:
            resp = requests.get(census.endpoint, params=params, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            headers = [h.upper() for h in data[0]]
            rows = data[1:]
            df = pd.DataFrame(rows, columns=headers)
            df["FIPS"] = df["STATE"].str.zfill(2) + df["COUNTY"].str.zfill(3)
            df["POP"] = pd.to_numeric(df["POP"], errors="coerce")
            return df
        except requests.RequestException as exc:
            logger.warning(f"Census API attempt {attempt}/{cdc.max_retries} failed: {exc}")
            if attempt < cdc.max_retries:
                time.sleep(cdc.backoff_seconds ** attempt)
    raise RuntimeError(f"All {cdc.max_retries} attempts failed for Census API")


def ingest() -> int:
    logger.info("Starting US Census population ingestion")
    df = fetch_population()
    logger.info(f"Fetched {len(df)} county population records")
    rows = load_dataframe(df, table=TARGET_TABLE, schema=TARGET_SCHEMA, if_exists="replace")
    logger.info(f"Census population ingestion finished — {rows} rows loaded")
    return rows


if __name__ == "__main__":
    ingest()
