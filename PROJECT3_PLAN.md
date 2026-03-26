# Project 3 — Development Plan

## Overview

COVID-19 data intelligence platform integrating CDC and US Census data into Snowflake, orchestrated by Airflow, transformed with dbt, and visualized via Streamlit.

---

## Data Sources

### Source 1: CDC COVID-19 Cases with Geography

- **API:** SODA (no auth required)
- **Endpoint:** `https://data.cdc.gov/resource/n8mc-b4w4.json`
- **Fields:** state_fips_code, county_fips_code, case_month, age_group, sex, race, ethnicity, outcome, hospitalization
- **Volume:** Millions of records (paginate with `$limit` and `$offset`)
- **Update frequency:** Monthly
- **Snowflake table:** `RAW.RAW_COVID_CASES`

### Source 2: CDC COVID-19 Vaccinations by County

- **API:** SODA (no auth required)
- **Endpoint:** `https://data.cdc.gov/resource/8xkx-amqh.json`
- **Fields:** fips, recip_county, recip_state, date, administered_dose1_recip, series_complete_yes, booster_doses, census2019
- **Volume:** ~3,000+ counties × multiple dates
- **Update frequency:** Weekly (historically)
- **Snowflake table:** `RAW.RAW_VACCINATIONS`

### Source 3: US Census Population Estimates

- **API:** Census API (free key required — get at https://api.census.gov/data/key_signup.html)
- **Endpoint:** `https://api.census.gov/data/2023/pep/charv`
- **Fields:** POP, NAME, state, county (FIPS codes)
- **Volume:** ~3,200 counties
- **Update frequency:** Annual (static for this project)
- **Snowflake table:** `RAW.RAW_POPULATION`

### JOIN Keys

```
CDC Cases (state_fips_code + county_fips_code) → Census (state + county)
CDC Vaccinations (fips)                        → Census (state + county)
CDC Cases (state_fips_code)                    → CDC Vaccinations (recip_state)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Ingestion | Python (requests/httpx, pandas) |
| Warehouse | Snowflake |
| Modeling & Testing | dbt (dbt-snowflake) |
| Orchestration | Apache Airflow (local venv, no Docker) |
| Dashboard | Streamlit (connects to Snowflake) |
| Package Management | uv |
| Stretch Goal | FastAPI with Swagger docs |

---

## Team Roles

| Ingestion & Platform Lead | Modeling & Analytics Lead |
|---------------------------|--------------------------|
| Python ingestion scripts (CDC + Census APIs) | dbt models (staging → intermediate → marts) |
| Airflow DAGs | dbt tests (built-in + custom) |
| Snowflake raw layer loading | Streamlit dashboard |
| Error handling, logging, monitoring | Documentation |

**Shared:** Architecture decisions, integration tests, data contracts, presentation

---

## Snowflake Schema Structure

```sql
RAW          -- Landing zone (Python loads here)
STAGING      -- dbt staging models (1:1 with sources, light cleaning)
INTERMEDIATE -- dbt intermediate models (joins, business logic)
MARTS        -- dbt marts (analytics-ready, dashboard-facing)
```

---

## Project Structure

```
project3/
├── dags/
│   └── covid_pipeline_dag.py       -- Airflow DAG
├── src/
│   ├── __init__.py
│   ├── config.py                   -- Config and credentials
│   ├── ingest_covid_cases.py       -- CDC cases ingestion
│   ├── ingest_vaccinations.py      -- CDC vaccinations ingestion
│   ├── ingest_population.py        -- Census population ingestion
│   └── load_to_snowflake.py        -- Shared Snowflake loader
├── dbt_project/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_covid_cases.sql
│   │   │   ├── stg_vaccinations.sql
│   │   │   ├── stg_population.sql
│   │   │   └── sources.yml
│   │   ├── intermediate/
│   │   │   ├── int_cases_with_population.sql
│   │   │   └── int_vaccinations_with_population.sql
│   │   └── marts/
│   │       ├── mart_rolling_avg_cases.sql
│   │       ├── mart_case_fatality_rate.sql
│   │       ├── mart_cases_per_100k.sql
│   │       ├── mart_vaccination_vs_cases.sql
│   │       ├── mart_data_freshness.sql
│   │       └── schema.yml
│   ├── macros/
│   │   └── generate_schema_name.sql
│   └── dbt_project.yml
├── streamlit/
│   └── app.py                      -- Dashboard
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## Metrics

### Required (from assignment)

| # | Metric | dbt Model | Sources Used |
|---|--------|-----------|-------------|
| 1 | 7-day rolling average of new cases | `mart_rolling_avg_cases` | CDC Cases |
| 2 | Case fatality rate by region | `mart_case_fatality_rate` | CDC Cases |
| 3 | Cases per 100k population | `mart_cases_per_100k` | CDC Cases + Census |
| 4 | Data freshness by source | `mart_data_freshness` | Ingestion metadata |
| 5 | Vaccination coverage vs case rate | `mart_vaccination_vs_cases` | CDC Vaccination + CDC Cases + Census |

### Custom (at least 2 — choose from these)

| Metric | Description | Why it matters |
|--------|-------------|---------------|
| Hospitalization rate by age group | Hospitalizations / cases by age bracket | Identifies vulnerable populations |
| Vaccination equity index | Vaccination rates by SVI category (urban vs rural) | Highlights access disparities |
| Monthly case trend by state | Month-over-month case change by state | Shows pandemic trajectory |
| Booster adoption rate | Booster doses / series complete by county | Measures ongoing vaccine engagement |

---

## Airflow DAG Structure

```
ingest_covid_cases >> ingest_vaccinations >> ingest_population
          └──────────────┴──────────────────┘
                         │
                   dbt_run_staging
                         │
                  dbt_run_intermediate
                         │
                     dbt_run_marts
                         │
                      dbt_test
                         │
                  quality_report_task
```

**Schedule:** Daily or weekly (depending on source update frequency)

---

## Development Timeline (6 class days)

### Days 1-2: Architecture & Foundation

- [ ] Finalize data source selection and defend choice
- [ ] Set up GitHub repo under NSS org, add collaborator
- [ ] Set up Snowflake (warehouse, database, 4 schemas)
- [ ] Initialize project with `uv` and install dependencies
- [ ] Build Python ingestion scripts for all 3 sources
- [ ] Test API calls and confirm data shape
- [ ] Load sample data to Snowflake RAW layer
- [ ] Define data contracts between ingestion and dbt
- [ ] Set up Airflow environment (local venv)

### Days 3-4: Core Development

- [ ] **Ingestion Lead:** Wire up Airflow DAG with ingestion tasks
- [ ] **Ingestion Lead:** Add error handling, retry logic, logging
- [ ] **Ingestion Lead:** Implement incremental loading (don't re-download everything)
- [ ] **Modeling Lead:** Create dbt staging models (1:1 with raw tables)
- [ ] **Modeling Lead:** Create intermediate models (joins, business logic)
- [ ] **Modeling Lead:** Create marts models (all 5 required metrics + 2 custom)
- [ ] **Modeling Lead:** Add dbt tests (unique, not_null, accepted_values, custom)
- [ ] Integration sync: verify ingestion output matches dbt source expectations

### Days 5-6: Dashboard, Polish & Presentation

- [ ] Build Streamlit dashboard:
  - Overview page with KPIs
  - Geographic view (cases/vaccinations by state)
  - Metrics deep dive (filterable by region, time period)
  - Data quality page (freshness, test results)
- [ ] Cross-source validation and data reconciliation
- [ ] End-to-end system testing (trigger Airflow → data flows through)
- [ ] Write README and technical documentation
- [ ] Prepare presentation (20-25 min):
  - Architecture & team coordination
  - Technical challenges & solutions
  - Business impact & metrics rationale
  - Live demo
  - Collaboration reflection
  - Q&A prep

---

## Dependencies to Install

```bash
uv init
uv add requests httpx pandas snowflake-connector-python python-dotenv loguru
uv add dbt-snowflake
uv add apache-airflow
uv add streamlit plotly
uv add --dev ruff
```

---

## Key Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| CDC COVID data is stale/outdated | Accept weekly granularity. Pivot to Flu data (ILINet) if needed — coach approved this |
| CDC API rate limiting | Implement pagination with `$limit`/`$offset`, add retry logic with backoff |
| Large data volumes (millions of rows) | Use `$where` filters in SODA API to limit date range (last 3 years), load in batches |
| Mid-project requirement changes ("twists") | Keep architecture modular so adding a new source or metric is easy |
| Airflow setup issues | Airflow runs in local venv (no Docker). Fall back to manual `dbt run` if Airflow blocks progress |

---

## Reminder

- **Expect requirement changes mid-project** — the coach will introduce "twists" to simulate real stakeholders
- Keep the pipeline **automated** — Airflow should trigger everything
- Both team members must understand the **full system**, not just their piece
- **15-20 minute presentation** with live demo to industry panel
