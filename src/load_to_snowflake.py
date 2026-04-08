"""
Shared Snowflake loader used by all ingestion scripts.
"""

import snowflake.connector
import snowflake.connector.pandas_tools
import pandas as pd
from loguru import logger
from src.config import snowflake as sf_config


def get_connection() -> snowflake.connector.SnowflakeConnection:
    return snowflake.connector.connect(
        account=sf_config.account,
        user=sf_config.user,
        password=sf_config.password,
        warehouse=sf_config.warehouse,
        database=sf_config.database,
        schema=sf_config.raw_schema,
        role=sf_config.role,
        client_session_keep_alive=True,  # prevents token expiry on long ingestion runs
        session_parameters={"QUERY_TAG": "covid_pipeline"},
    )


def load_dataframe(
    df: pd.DataFrame,
    table: str,
    schema: str = "RAW",
    if_exists: str = "append",
) -> int:
    """
    Write a pandas DataFrame to a Snowflake table.

    Parameters
    ----------
    df        : DataFrame to load
    table     : Target table name (unqualified)
    schema    : Target schema (default RAW)
    if_exists : 'append' (default) or 'replace' (truncates first)

    Returns
    -------
    int : Number of rows written
    """
    if df.empty:
        logger.warning(f"Empty DataFrame — nothing to load into {schema}.{table}")
        return 0

    conn = get_connection()
    try:
        full_table = f"{sf_config.database}.{schema}.{table}"

        if if_exists == "replace":
            conn.cursor().execute(f"TRUNCATE TABLE IF EXISTS {full_table}")

        success, nchunks, nrows, _ = snowflake.connector.pandas_tools.write_pandas(
            conn=conn,
            df=df,
            table_name=table.upper(),
            schema=schema.upper(),
            database=sf_config.database.upper(),
            auto_create_table=True,
            overwrite=(if_exists == "replace"),
            quote_identifiers=False,
        )

        if success:
            logger.info(f"Loaded {nrows} rows into {full_table} ({nchunks} chunks)")
        else:
            logger.error(f"write_pandas reported failure for {full_table}")

        return nrows
    finally:
        conn.close()
