# Project 3 — Full Pipeline with Team Orchestration

**Dataset:** COVID-19 Government Data Sources **Duration:** 4–5 days **Team Size:** 2 people 

---

## 🎯 Project Objectives

By the end of this project, teams will have demonstrated:

- **End-to-end pipeline** integrating multiple government data sources into Snowflake with production orchestration  
- **Team collaboration** with coordinated architecture decisions and integrated component development  
- **Enterprise-grade data quality** with validation across all pipeline stages  
- **Stakeholder-ready deliverables** including a Streamlit dashboard and team presentation to an industry panel

---

## ⚡ Team Orchestration

This project demonstrates coordination on complex data engineering architecture:

- **2-person teams** making coordinated technical decisions for an integrated system  
- **Production complexity** — real government datasets with authentic data quality and integration challenges  
- **Stakeholder presentation** — professional communication of technical capabilities and business impact  
- **Enterprise readiness** — demonstrating ability to work as a coordinated pair on production-scale projects

---

## 📚 Business Scenario

**Client:** National Public Health Analytics Consortium

The consortium needs a COVID-19 data intelligence platform integrating multiple government sources to support public health decision-making.

**Business Requirements:**

- Multi-source integration — at least two government data sources, coordinated into a unified model  
- Geographic intelligence — regional analysis with demographic correlation and trend identification (depth depends on chosen sources)  
- Regulatory compliance — audit trails, data lineage, and quality reporting for government oversight

**Technical Challenges:**

- Multiple government APIs, file formats, and update schedules requiring coordinated ingestion  
- Inconsistent data quality across sources requiring sophisticated validation and remediation  
- 2-person architecture requiring clear integration interfaces and collaborative development

---

## 🏗️ Tech Stack

| Layer | Technology |
| :---- | :---- |
| Ingestion & Transformation (Python) | Python 3.12+, requests/httpx, pandas/polars |
| Warehouse | Snowflake |
| Modeling & Testing | dbt (dbt-snowflake adapter) |
| Orchestration | Apache Airflow |
| Dashboard | Streamlit |
| **Stretch Goal** | **FastAPI with Swagger docs** |

---

## 🗂️ Data Sources

Teams must integrate **at least two** of the following sources. Choose the ones that best support the metrics and story you want to tell. More sources \= more integration complexity \= more impressive, but depth matters more than breadth.

### 1\. CDC COVID-19 Data APIs

- Multiple endpoints with different schemas and authentication requirements  
- Daily updates with historical data, millions of records  
- Challenges: rate limiting, schema evolution, nested JSON structures

### 2\. State Health Department Data

- 50+ state portals with varying formats and update schedules  
- CSV downloads ranging from thousands to millions of records per state  
- Challenges: schema inconsistencies, data quality variations

### 3\. International Data Sources (WHO/ECDC)

- International standards and formats different from US sources  
- Country-level aggregations with multiple time series and demographic breakdowns  
- Challenges: population adjustments, different reporting standards

### 4\. US Census Demographic Data

- API integration with geographic crosswalk requirements  
- County-level demographics with multiple variables  
- Challenges: geographic boundary changes, correlation analysis

Your Day 1 architecture plan should include which sources you're using and why — defend the choice.

---

## 👥 Team Architecture

```
┌─────────────────────┐    ┌─────────────────────┐
│  Ingestion &        │    │  Modeling &          │
│  Platform Lead      │    │  Analytics Lead      │
│                     │    │                      │
│  Python ingestion   │────│  dbt modeling        │
│  Airflow DAGs       │    │  Data quality tests  │
│  Snowflake loading  │    │  Streamlit dashboard │
│  Monitoring         │    │  Documentation       │
└─────────────────────┘    └─────────────────────┘
            │                        │
┌───────────────────────────────────────────────┐
│            Shared Responsibilities            │
│  Architecture decisions • Integration tests   │
│  Data contracts • Stakeholder presentation    │
└───────────────────────────────────────────────┘
```

Both team members should understand the full system. The role split is about primary ownership, not silos.

---

## 📅 Project Timeline

### Architecture & Foundation

- Collaborative architecture design with clear role definition and integration interfaces  
- Data source analysis and assignment with coordination for cross-dependencies  
- Tech stack setup: Snowflake warehouse, Airflow environment, dbt project scaffold, shared repo  
- Sample data processing across all sources with quality baseline established  
- Integration interface definition (data contracts between ingestion and modeling layers)

### Core Development

- **Ingestion & Platform Lead:** Multi-source Python ingestion scripts, Airflow DAG wiring, Snowflake raw layer loading, error handling and retry logic  
- **Modeling & Analytics Lead:** dbt staging/intermediate/marts layer, dbt tests (built-in \+ custom), business logic implementation  
- Regular sync points ensuring components integrate — ingestion output matches dbt source expectations  
- Integration testing across the full pipeline path

### Metrics, Dashboard & Polish

- Build out your metrics layer in dbt marts (see **Suggested Metrics** below)  
- Cross-source validation and data reconciliation  
- **Streamlit dashboard** with public health KPIs and geographic visualization — [Streamlit documentation](https://docs.streamlit.io/)  
- Technical documentation: architecture explanation, operational procedures, troubleshooting  
- Presentation preparation

#### Suggested Metrics

Start with these, pick a few of these, and then **create at least two additional metrics** that you think would be useful for public health decision-makers. Be ready to explain why you chose them.

| Metric | Description |
| :---- | :---- |
| 7-day rolling average of new cases | Smooths daily reporting noise, standard public health reporting metric |
| Case fatality rate by region | Deaths / confirmed cases — highlights regional healthcare capacity differences |
| Cases per 100k population | Population-normalized comparison across counties or states of different sizes |
| Data freshness by source | How stale is each source? Critical for trust and operational monitoring |
| Vaccination coverage vs case rate correlation | If using CDC \+ Census data — do higher-vaccinated areas show different case trajectories? |

Your custom metrics should come from exploring the data and thinking about what a public health official would actually want to see. Document the rationale.

### Production Readiness & Presentation

- End-to-end system testing with realistic volumes, production deployment validation, monitoring and alerting setup, final integration testing  
- Coordinated team presentation (20–25 minutes) to industry panel, live technical demonstration, Q\&A

---

## 🚀 Stretch Goal: FastAPI with Swagger Docs

Teams that complete the core deliverables can extend the platform with a data API layer. Start with the [FastAPI documentation](https://fastapi.tiangolo.com/) — it's excellent and you should be able to get a working API up by reading the docs and experimenting.

- **FastAPI application** serving key analytics endpoints (county-level stats, trend data, quality metrics)  
- **Auto-generated Swagger documentation** via FastAPI's built-in OpenAPI support  
- **Practical value:** demonstrates how the same dbt-modeled data can serve both dashboards and programmatic consumers  
- Endpoints might include: `/api/v1/counties/{fips}/summary`, `/api/v1/trends`, `/api/v1/quality/status`

---

## 🎤 Team Presentation Requirements

**Coordinated Team Presentation (20–25 minutes)**

### Section 1: Architecture & Team Coordination

- Architecture decisions — how the pair coordinated across ingestion, modeling, orchestration, and delivery  
- Integration strategy — data contracts, shared conventions, how individual work became a cohesive system  
- Technology choices and rationale

### Section 2: Technical Challenges & Solutions

- Multi-source integration complexity and how the team handled it  
- Data quality coordination across sources  
- Airflow orchestration decisions  
- Performance and cost considerations in Snowflake

### Section 3: Business Impact & Public Health Value

- Meaningful analytics derived from integrated data  
- Your chosen metrics — both the suggested ones and the ones you created — and why they matter  
- How the platform supports public health decision-making

### Section 4: Live Demonstration

- End-to-end pipeline execution — trigger Airflow DAG, show data flowing through  
- Streamlit dashboard walkthrough with public health insights  
- dbt test results and quality validation showcase  
- *(If completed)* FastAPI Swagger docs and live endpoint calls

### Section 5: Collaboration Reflection

- How individual contributions created a cohesive system  
- What worked, what was hard, what you'd do differently  
- Lessons for scaling data engineering teams

### Section 6: Q\&A

- Architecture and scalability questions from industry panel  
- Team coordination and process questions

---

## ✅ Success Criteria

### Technical

- Chosen data sources successfully integrated into Snowflake with clear rationale for selection  
- dbt models with comprehensive testing across staging, intermediate, and marts layers  
- Airflow DAGs orchestrating the full pipeline reliably  
- Streamlit dashboard delivering meaningful public health insights  
- Production-grade error handling, logging, and monitoring

### Team Collaboration

- Clear individual responsibilities integrated into a cohesive system  
- Both team members can explain the full architecture and any component  
- Effective coordination — data contracts honored, integration points clean  
- Shared ownership of quality and documentation

### Business Impact

- Decision support capabilities demonstrated through the Streamlit dashboard  
- Suggested metrics implemented plus custom metrics with documented rationale  
- Audit trails and data lineage supporting regulatory requirements  
- Architecture that could scale to a larger team

### Professional

- Effective team presentation to industry panel  
- Successful Q\&A demonstrating depth of understanding  
- Technical documentation enabling operational handoff

---

## 🛠️ Implementation Guidance

### Suggested Snowflake Schema Structure

```
RAW          → Landing zone for ingested data (Python loads here)
STAGING      → dbt staging models (1:1 with sources, light cleaning)
INTERMEDIATE → dbt intermediate models (joins, business logic)
MARTS        → dbt marts (analytics-ready, dashboard-facing)
```

### Airflow DAG Structure (example — adjust for your chosen sources)

```
ingest_source_a >> ingest_source_b
    └──────────────┘
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

### Streamlit Dashboard Sections

- **Overview:** Key public health KPIs from your suggested and custom metrics  
- **Geographic:** Regional or county-level comparisons (if using geographic data)  
- **Metrics Deep Dive:** Selectable metrics with filtering by region, time period, or source  
- **Data Quality:** Pipeline health, freshness by source, validation pass rates

---

## 📋 Resources

- COVID-19 government datasets with realistic complexity across all specified sources  
- Geographic reference data including county-level demographics and boundary files  
- Lab 4 orchestration templates adapted for 2-person coordination  
- Team coordination guidance and industry mentor availability  
- Presentation coaching for effective delivery to industry professionals

