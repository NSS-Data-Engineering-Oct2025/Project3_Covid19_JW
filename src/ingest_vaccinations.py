"""
CDC COVID-19 Vaccinations by County ingestion.
Endpoint: https://data.cdc.gov/resource/8xkx-amqh.json  (SODA, no auth)
Target:   RAW.RAW_VACCINATIONS
"""

from src.config import cdc
from src.soda_ingestor import paginate_and_load

TARGET_TABLE = "RAW_VACCINATIONS"
TARGET_SCHEMA = "RAW"


def ingest(max_pages: int | None = None) -> int:
    """
    Paginate through the CDC vaccinations API and load all records into Snowflake.

    Parameters
    ----------
    max_pages : page cap for smoke tests (None = load all)

    Returns
    -------
    int : Total rows loaded
    """
    return paginate_and_load(
        endpoint=cdc.vaccinations_endpoint,
        target_table=TARGET_TABLE,
        target_schema=TARGET_SCHEMA,
        order_by="date DESC",
        source_name="CDC vaccinations",
        max_pages=max_pages,
    )


if __name__ == "__main__":
    ingest(max_pages=1)
