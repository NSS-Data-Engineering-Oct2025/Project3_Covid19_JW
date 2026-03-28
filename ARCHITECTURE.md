# Project Architecture — COVID-19 Intelligence Platform

## What We Are Building

A data pipeline that automatically pulls COVID-19 data from U.S. government sources,
stores it in Snowflake, transforms it with dbt, and displays insights through a
Streamlit dashboard — all orchestrated by Apache Airflow.

---

## Why We Chose These Data Sources

| Source | Why |
|--------|-----|
| **CDC COVID-19 Cases** (SODA API) | Primary dataset. Contains case-level records with geography, demographics, and outcomes. No authentication required. |
| **CDC COVID-19 Vaccinations** (SODA API) | Allows us to correlate vaccination coverage with case rates by county — a key public health question. |
| **U.S. Census Population Estimates** | Needed to normalize case counts by population (cases per 100k). Without this, comparing a large city to a small town is not meaningful. |

All three sources can be joined using the **FIPS code** — a 5-digit standard geographic
identifier for every U.S. county (2 digits for state + 3 digits for county).

---

## Why We Chose This Tech Stack

| Tool | Role | Why |
|------|------|-----|
| **Python** | Data ingestion | Flexible, great library support for APIs and Snowflake |
| **Snowflake** | Data warehouse | Cloud-native, scales automatically, integrates natively with dbt |
| **dbt** | Data transformation | Keeps transformation logic in SQL, adds automatic testing and documentation |
| **Apache Airflow** | Orchestration | Automates the full pipeline on a schedule with retries and logging |
| **Streamlit** | Dashboard | Python-native, connects directly to Snowflake, fast to build |
| **uv** | Package management | Faster and more reliable than pip for managing Python environments |

---

## How the Data Flows

```
Government APIs
      │
      ▼
Python ingestion scripts (src/)
  - ingest_covid_cases.py
  - ingest_vaccinations.py
  - ingest_population.py
      │
      ▼
Snowflake RAW schema
  - RAW_COVID_CASES
  - RAW_VACCINATIONS
  - RAW_POPULATION
      │
      ▼
dbt STAGING schema (views)
  - Clean data types
  - Normalize FIPS codes
  - Remove nulls and junk rows
      │
      ▼
dbt INTERMEDIATE schema (views)
  - Join cases + population
  - Join vaccinations + population
      │
      ▼
dbt MARTS schema (tables)
  - Final metrics ready for the dashboard
      │
      ▼
Streamlit Dashboard
  - Overview KPIs
  - Geographic map
  - Metrics deep dive
  - Data quality monitor
```

---

## Snowflake Schema Design

We use 4 schemas to keep each stage of the pipeline separate and traceable:

| Schema | Purpose | Who writes here |
|--------|---------|-----------------|
| `RAW` | Raw data exactly as received from APIs | Python |
| `STAGING` | Cleaned and typed data, 1:1 with raw tables | dbt |
| `INTERMEDIATE` | Joined data across sources | dbt |
| `MARTS` | Final analytics-ready metrics | dbt |

Separating layers means: if a metric is wrong, we can trace the problem to the exact
layer where it happened.

---

## Metrics We Plan to Deliver

| Metric | Business Question |
|--------|------------------|
| 3-month rolling average of new cases | Is the pandemic getting better or worse? |
| Case fatality rate by state | Which regions have worse health outcomes? |
| Cases per 100k population | How do counties of different sizes compare fairly? |
| Vaccination coverage vs case rate | Did higher vaccination lead to fewer cases? |
| Data freshness by source | Can we trust that the data is current? |
| Booster adoption rate (custom) | How engaged is each region with ongoing vaccination? |

---

## Expected Outcome

At the end of the project we will have:

1. An **automated pipeline** that runs weekly without manual intervention
2. A **Snowflake warehouse** with clean, tested, analytics-ready data
3. A **Streamlit dashboard** that a public health official could use to make decisions
4. **dbt tests** that automatically alert us if data quality drops
5. A **20-minute presentation** with live demo for the industry panel

---

## Team Role Split

| Wilmer | Jay |
|--------|-----|
| Python ingestion scripts | dbt staging and intermediate models |
| Airflow DAG wiring | dbt marts and tests |
| Snowflake raw layer loading | Streamlit dashboard |
| Error handling and logging | Documentation |

Both team members understand the full system. The split is about primary ownership,
not silos.
