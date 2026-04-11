# COVID-19 Intelligence Platform
## Team Presentation — Data Engineering Project 3
**National Public Health Analytics Consortium**
Duration: 20–25 minutes

---

## SLIDE 1 — Title

**COVID-19 Intelligence Platform**
*Integrating Government Data for Public Health Decision-Making*

- Team: Wilmer Saenz & Jay
- Stack: Python · Snowflake · dbt · Airflow · Streamlit
- Data: CDC APIs + US Census Bureau

---

## SECTION 1: Architecture & Team Coordination (5 min)

### SLIDE 2 — Data Sources & Why We Chose Them

| Source | What It Provides | Why |
|---|---|---|
| CDC COVID-19 Cases API | 23M+ individual case records | Granular clinical data (hospitalization, ICU, death) |
| CDC Vaccinations API | County-level vaccination rates | Enables correlation analysis with case outcomes |
| US Census Population Estimates | County demographics & population | Normalizes metrics across counties of different sizes |

**Key decision:** All three sources share a common FIPS geographic code — our join key across the entire pipeline.

---

### SLIDE 3 — System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  DATA SOURCES                        │
│   CDC Cases API  │  CDC Vaccines API  │  Census API  │
└────────┬─────────┴──────────┬─────────┴──────┬───────┘
         │                   │                 │
         ▼                   ▼                 ▼
┌─────────────────────────────────────────────────────┐
│          PYTHON INGESTION LAYER (src/)               │
│  ingest_covid_cases.py  │  ingest_vaccinations.py   │
│  ingest_population.py   │  load_to_snowflake.py     │
│  Retry logic · Pagination · Error handling           │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              SNOWFLAKE — COVID_DB                    │
│  RAW schema        → Landing zone (raw API data)    │
│  STAGING schema    → Cleaned, typed, normalized      │
│  INTERMEDIATE schema → Joins & business logic        │
│  MARTS schema      → Analytics-ready tables          │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              dbt TRANSFORMATION LAYER                │
│  12 models · 26 tests · 3 custom standalone tests   │
└──────────────────────┬──────────────────────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
┌─────────────────┐   ┌─────────────────────────────┐
│  AIRFLOW DAG    │   │  STREAMLIT DASHBOARD         │
│  Weekly schedule│   │  4 pages · 7 metrics         │
│  Orchestration  │   │  Live Snowflake connection   │
└─────────────────┘   └─────────────────────────────┘
```

---

### SLIDE 4 — Team Role Split

| Wilmer | Jay |
|---|---|
| Python ingestion scripts | dbt package setup (dbt_utils) |
| Snowflake schema design | print_table.py utility |
| dbt staging/intermediate/marts | Staging model review |
| Custom metrics (hospitalization, severity) | Pipeline coordination |
| Streamlit dashboard | README documentation |
| Airflow DAG | — |

**Shared:** Architecture decisions, data contracts, Snowflake account, integration testing

---

### SLIDE 5 — Data Contract (Integration Interface)

The contract between ingestion and dbt:

```
RAW.RAW_COVID_CASES must contain:
  - state_fips_code, county_fips_code (for FIPS join key)
  - case_month (format YYYY-MM)
  - hosp_yn, icu_yn, death_yn (clinical flags)
  - current_status, symptom_status

RAW.RAW_VACCINATIONS must contain:
  - fips (5-digit county code)
  - series_complete_pop_pct
  - booster_doses_vax_pct

RAW.RAW_POPULATION must contain:
  - county_fips (5-digit)
  - population (integer)
  - county_name
```

---

## SECTION 2: Technical Challenges & Solutions (5 min)

### SLIDE 6 — Challenge 1: API Schema Discovery

**Problem:** CDC API column names were different from documentation.
- Expected: `outcome`, `hospitalization`
- Actual: `death_yn`, `hosp_yn`, `icu_yn` (Yes/No fields)

**Solution:**
- Ran `DESCRIBE TABLE` in Snowflake after first ingestion
- Updated `stg_covid_cases.sql` to map actual columns
- Added binary flags: `is_death`, `is_hospitalized`, `is_icu`

---

### SLIDE 7 — Challenge 2: Snowflake Session Expiry on Large Loads

**Problem:** Loading 23M rows took ~2.5 hours → Snowflake authentication token expired mid-ingestion.

**Solution:**
```python
snowflake.connector.connect(
    ...
    client_session_keep_alive=True,  # renews token automatically
)
```

**Result:** Pipeline can now run full loads without interruption.

---

### SLIDE 8 — Challenge 3: dbt Schema Naming

**Problem:** dbt by default creates schemas like `WILMER_STAGING` instead of `STAGING`.

**Solution:** Custom macro `generate_schema_name.sql` that overrides dbt's default behavior:
```sql
{% macro generate_schema_name(custom_schema_name, node) %}
    {{ custom_schema_name | trim }}
{% endmacro %}
```

**Result:** Clean schema names: `RAW`, `STAGING`, `INTERMEDIATE`, `MARTS`.

---

### SLIDE 9 — Challenge 4: Team Coordination on Shared Snowflake

**Problem:** Two people sharing one Snowflake account — risk of duplicate data if both run ingestion.

**Solution:**
- One person owns ingestion (Wilmer loaded the full dataset)
- Jay runs only `dbt run` and `dbt test` — reads existing data
- Communication via Slack before any destructive operations (TRUNCATE)

---

## SECTION 3: Business Impact & Public Health Value (5 min)

### SLIDE 10 — Metrics Implemented

**5 Suggested Metrics:**

| Metric | dbt Model | Business Value |
|---|---|---|
| 3-month rolling avg cases | `mart_rolling_avg_cases` | Smooths reporting noise — standard public health KPI |
| Case fatality rate | `mart_case_fatality_rate` | Highlights regional healthcare capacity differences |
| Cases per 100k population | `mart_cases_per_100k` | Fair comparison across counties of different sizes |
| Data freshness by source | `mart_data_freshness` | Operational trust — is the data current? |
| Vaccination vs case rate | `mart_vaccination_vs_cases` | Measures effectiveness of vaccination campaigns |

---

### SLIDE 11 — Custom Metrics (Our Innovation)

**Custom Metric 1: Hospitalization Rate**
- Formula: `total_hospitalizations / total_cases × 100`
- Model: `mart_hospitalization_rate`
- **Why:** CFR tells you who died, but hospitalization rate tells you how much the healthcare system is under stress — even when people survive.

**Custom Metric 2: Severity Index**
- Formula: `hosp_rate × 0.4 + icu_rate × 0.4 + cfr × 0.2`
- Model: `mart_severity_index`
- **Why:** A single composite score to rank counties by overall disease severity — useful for resource allocation decisions. ICU burden weighted highest because it's the most constrained resource.

---

### SLIDE 12 — Data Quality Layer

**26 dbt tests total:**
- `not_null` on all key columns
- `unique` on primary keys
- `accepted_values` on categorical fields
- **3 custom standalone SQL tests:**
  - `assert_cases_per_100k_not_negative` — no negative rates
  - `assert_case_fatality_rate_in_range` — CFR between 0% and 100%
  - `assert_case_month_after_2020` — no pre-pandemic data

**Result: 25 PASS, 1 WARN** (known duplicate in vaccination data — partial load)

---

## SECTION 4: Live Demonstration (5 min)

### SLIDE 13 — Demo Script

**Step 1: Show the pipeline code**
- Open `main.py` — the manual orchestrator
- Show `src/ingest_covid_cases.py` — pagination + retry logic

**Step 2: Show Airflow DAG**
- Open `dags/covid_pipeline_dag.py`
- Explain the task dependency graph:
  ```
  [ingest_cases, ingest_vaccinations, ingest_population]
       → dbt_staging → dbt_intermediate → dbt_marts
       → dbt_test → quality_report
  ```

**Step 3: Show Streamlit Dashboard** (localhost:8501)
- Overview: 4.2M cases, 27k deaths, 0.82% CFR
- Geographic: choropleth map + vaccination scatter
- Metrics Deep Dive: CFR over time, top counties, custom metrics ★
- Data Quality: freshness status + test results

**Step 4: Show dbt test results**
```bash
dbt test  →  25 PASS, 1 WARN, 0 ERROR
```

---

## SECTION 5: Collaboration Reflection (3 min)

### SLIDE 14 — What Worked

- **Clear ownership**: Wilmer owned ingestion + dbt + dashboard, Jay owned utilities + review
- **Shared Snowflake**: One account, one source of truth — no data silos
- **Git branches**: Each working independently (`test2-w`, `print`) without breaking each other
- **`main.py` as dev orchestrator**: Allowed full pipeline testing without Airflow overhead

---

### SLIDE 15 — What Was Hard

- **API schema discovery**: Had to ingest first, then inspect with `DESCRIBE TABLE` — real-world data engineering
- **Snowflake session management**: Token expiry on long loads — solved with `client_session_keep_alive`
- **Coordinate without duplicating**: Needed explicit communication about who runs ingestion
- **dbt folder naming**: Different conventions between branches (`dbt_project/` vs `covid_19/`) — resolved by aligning on `covid_19/`

---

### SLIDE 16 — What We'd Do Differently

- Start with a **data contract document** before writing any code
- Use **Snowflake stages** for raw file landing instead of direct API → Snowflake
- Set up **Airflow from day 1** instead of using `main.py` as a workaround
- Add **incremental dbt models** to avoid full refreshes on large tables

---

## SECTION 6: Q&A Prep

### SLIDE 17 — Anticipated Questions

**Q: Why not use Spark or a distributed system?**
A: The dataset (~23M rows) fits comfortably in Snowflake's compute. Snowflake's virtual warehouse scales horizontally when needed — adding Spark would add complexity without benefit at this scale.

**Q: How would this scale to 50 states + daily updates?**
A: The Airflow DAG is already scheduled `@weekly`. For daily: change `schedule_interval="@daily"`. For 50 states: the FIPS-based model handles all states — we just need more data in RAW, dbt handles the rest automatically.

**Q: How do you ensure data quality in production?**
A: Three layers — (1) Python retry logic catches API failures, (2) dbt tests run after each transformation layer, (3) `mart_data_freshness` shows staleness to operators. An Airflow alert would notify on test failures.

**Q: Why dbt instead of writing SQL directly?**
A: dbt gives us version control on SQL, dependency management between models, built-in testing, and documentation. A raw SQL script in a Jupyter notebook can't be tested, scheduled, or reviewed in a PR.

**Q: What does the Severity Index actually tell a public health official?**
A: It combines three clinical signals (hospitalization 40%, ICU 40%, CFR 20%) into a single ranking. A county with severity_index > 5 needs immediate resource attention. The weights reflect that ICU capacity is the most constrained resource — when ICUs fill up, outcomes worsen rapidly.

---

*End of presentation — Thank you*
