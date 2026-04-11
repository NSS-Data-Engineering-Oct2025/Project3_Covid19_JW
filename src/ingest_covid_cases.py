"""
CDC COVID-19 Cases with Geography ingestion.
Endpoint: https://data.cdc.gov/resource/n8mc-b4w4.json  (SODA, no auth)
Target:   RAW.RAW_COVID_CASES
"""

from src.config import cdc
from src.soda_ingestor import paginate_and_load

TARGET_TABLE = "RAW_COVID_CASES"
TARGET_SCHEMA = "RAW"


def ingest(max_pages: int | None = None) -> int:
    """
    Paginate through the CDC cases API and load all records into Snowflake.

    Parameters
    ----------
    max_pages : page cap for smoke tests (None = load all)

    Returns
    -------
    int : Total rows loaded
    """
    return paginate_and_load(
        endpoint=cdc.cases_endpoint,
        target_table=TARGET_TABLE,
        target_schema=TARGET_SCHEMA,
        order_by="case_month DESC",
        source_name="CDC COVID cases",
        max_pages=max_pages,
    )


if __name__ == "__main__":
    ingest(max_pages=2)  # smoke test: 2 pages = 100k rows
