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
Copy-Item dbt_project\profiles.yml.example $HOME\.dbt\profiles.yml
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
cd dbt_project
dbt debug          # verify connection
dbt run            # build all models
dbt test           # run all tests
```

### 7. Launch dashboard

```powershell
streamlit run streamlit/app.py
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

| Metric | dbt Model |
|--------|-----------|
| 3-month rolling avg of new cases | `mart_rolling_avg_cases` |
| Case fatality rate by state | `mart_case_fatality_rate` |
| Cases per 100k population | `mart_cases_per_100k` |
| Vaccination coverage vs case rate | `mart_vaccination_vs_cases` |
| Data freshness by source | `mart_data_freshness` |
| Booster adoption rate (custom) | `mart_vaccination_vs_cases` |

---

## Project Structure

```bash
├── dags/                   Airflow DAG
├── src/                    Python ingestion scripts
├── dbt_project/            dbt project (models, macros, tests)
│   ├── models/staging/
│   ├── models/intermediate/
│   └── models/marts/
├── streamlit/              Streamlit dashboard
├── .env.example            Environment variables template
├── pyproject.toml          Python dependencies (uv)
└── readme.md
```
