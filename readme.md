# COVID-19 Intelligence Platform — Project 3

Data Engineering Bootcamp — NSS cohort  
**Stack:** Python · Snowflake · dbt · Apache Airflow · Streamlit

---

## Architecture

```
CDC SODA API ──┐
               ├─► Python ingestion (src/) ─► Snowflake RAW
Census API ────┘
                                                    │
                                              dbt STAGING (views)
                                                    │
                                          dbt INTERMEDIATE (views)
                                                    │
                                            dbt MARTS (tables)
                                                    │
                                    Streamlit Dashboard ◄── Airflow DAG
```

**Snowflake schemas:** `RAW` · `STAGING` · `INTERMEDIATE` · `MARTS`

---

## Quick Start

### 1. Install dependencies
```powershell
uv sync
```

### 2. Configure credentials
```powershell
Copy-Item .env.example .env
# Edit .env with your Snowflake password and Census API key
```

### 3. Configure dbt
```powershell
Copy-Item covid_19\profiles.yml.example $HOME\.dbt\profiles.yml
# Edit ~/.dbt/profiles.yml and set SNOWFLAKE_PASSWORD
```

### 4. Create Snowflake objects
Run in Snowflake worksheet:
```sql
CREATE DATABASE IF NOT EXISTS COVID_DB;
CREATE SCHEMA IF NOT EXISTS COVID_DB.RAW;
CREATE SCHEMA IF NOT EXISTS COVID_DB.STAGING;
CREATE SCHEMA IF NOT EXISTS COVID_DB.INTERMEDIATE;
CREATE SCHEMA IF NOT EXISTS COVID_DB.MARTS;
```

### 5. Test ingestion (smoke test — 2 pages only)
```powershell
uv run python -m src.ingest_covid_cases
uv run python -m src.ingest_vaccinations
uv run python -m src.ingest_population
```

### 6. Run dbt
```powershell
cd covid_19
uv run dbt deps     # install dbt_utils
uv run dbt debug    # verify connection
uv run dbt run      # build all models
uv run dbt test     # run all tests
```

### 7. Launch dashboard
```powershell
uv run streamlit run streamlit/app.py
```

---

## Data Sources

| Source | Endpoint | Table | Update Freq |
|--------|----------|-------|-------------|
| CDC COVID Cases | `data.cdc.gov/resource/n8mc-b4w4.json` | `RAW.RAW_COVID_CASES` | Monthly |
| CDC Vaccinations | `data.cdc.gov/resource/8xkx-amqh.json` | `RAW.RAW_VACCINATIONS` | Weekly |
| US Census PEP 2023 | `api.census.gov/data/2023/pep/charv` | `RAW.RAW_POPULATION` | Annual |

---

## Metrics

| Metric | dbt Model | Type |
|--------|-----------|------|
| 3-month rolling avg of new cases | `mart_rolling_avg_cases` | Built-in |
| Case fatality rate by state | `mart_case_fatality_rate` | Built-in |
| Cases per 100k population | `mart_cases_per_100k` | Built-in |
| Vaccination coverage vs case rate | `mart_vaccination_vs_cases` | Built-in |
| Data freshness by source | `mart_data_freshness` | Built-in |
| Hospitalization rate by state | `mart_hospitalization_rate` | Custom |
| Severity index by county | `mart_severity_index` | Custom |

---

## Project Structure

```
├── dags/                   Airflow DAG
├── src/                    Python ingestion scripts
│   ├── config.py           Centralized configuration (@dataclass)
│   ├── soda_ingestor.py    Shared CDC pagination & retry logic
│   ├── load_to_snowflake.py Snowflake loader
│   ├── ingest_covid_cases.py
│   ├── ingest_vaccinations.py
│   └── ingest_population.py
├── covid_19/               dbt project
│   ├── models/staging/
│   ├── models/intermediate/
│   ├── models/marts/
│   ├── macros/
│   └── tests/              Custom data quality tests
├── streamlit/              Streamlit dashboard
├── .env.example            Environment variables template
├── pyproject.toml          Python dependencies (uv)
└── readme.md
```
