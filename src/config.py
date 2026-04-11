"""
Centralized configuration loaded from .env.
All other modules import from here — never read os.environ directly.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class SnowflakeConfig:
    account: str = field(default_factory=lambda: os.environ["SNOWFLAKE_ACCOUNT"])
    user: str = field(default_factory=lambda: os.environ["SNOWFLAKE_USER"])
    password: str = field(default_factory=lambda: os.environ["SNOWFLAKE_PASSWORD"])
    warehouse: str = field(default_factory=lambda: os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"))
    database: str = field(default_factory=lambda: os.environ.get("SNOWFLAKE_DATABASE", "COVID_DB"))
    role: str = field(default_factory=lambda: os.environ.get("SNOWFLAKE_ROLE", "SYSADMIN"))
    raw_schema: str = "RAW"


@dataclass(frozen=True)
class CDCConfig:
    cases_endpoint: str = "https://data.cdc.gov/resource/n8mc-b4w4.json"
    vaccinations_endpoint: str = "https://data.cdc.gov/resource/8xkx-amqh.json"
    page_size: int = 50_000
    max_retries: int = 3
    backoff_seconds: float = 2.0


@dataclass(frozen=True)
class CensusConfig:
    api_key: str = field(default_factory=lambda: os.environ.get("CENSUS_API_KEY", ""))
    endpoint: str = "https://api.census.gov/data/2023/pep/charv"


snowflake = SnowflakeConfig()
cdc = CDCConfig()
census = CensusConfig()
