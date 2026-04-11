# Project 4 — Context File for AI Assistant
## Read this before starting any work

---

## 1. Student Profile

**Name:** Wilmer Saenz  
**Username:** WILMERSAENZ81  
**Level:** Data Engineering bootcamp student — intermediate level  
**OS:** Windows 11, PowerShell  
**Package manager:** `uv` (NOT pip — always use `uv run` or `uv add`)  
**Editor:** Cursor IDE  
**Language preference:** Explanations in **Spanish**, all project files in **English**  

**Experience:**
- Completed Project 3 (COVID-19 pipeline): Python ingestion, Snowflake, dbt (staging/intermediate/marts), Streamlit dashboard, Airflow DAG skeleton
- Comfortable with: Git, pandas, loguru, snowflake-connector, dbt models and tests, dotenv
- NEW in Project 4: WebSockets, RabbitMQ, PostgreSQL, DuckDB, Metabase, real-time streaming

---

## 2. Working Style & Preferences

- **Step by step:** Wilmer prefers manual, visible steps — do not run commands automatically, always show what to run and why
- **Explanations in Spanish:** When explaining concepts or answering questions, use Spanish. Code, comments, and files stay in English
- **No surprises:** Always explain what a command does before asking to run it
- **Commit after each milestone:** Don't accumulate too many changes before committing
- **Ask before big decisions:** If there are multiple valid approaches, present the options with trade-offs instead of just picking one
- **Academic + industry balance:** This is an academic project that simulates industry standards. Don't over-engineer, but do apply real patterns (retry logic, dataclasses, no hardcoded secrets, etc.)

---

## 3. Project 4 Overview

**Project:** Real-Time Crypto Streaming & Lakehouse Analytics  
**Type:** Individual project (no teammate)  
**Duration:** ~4 days  
**Client scenario:** A boutique quant trading firm needs real-time crypto analytics without querying the production database directly

**Full data flow:**
```
Coinbase WebSocket
      ↓
Python Producer (websockets)
      ↓
RabbitMQ (message broker / buffer)
      ↓
Python Consumer (background worker)
      ↓
PostgreSQL — Bronze (raw JSON)
      ↓
dbt — Silver (cleaned) → Gold (aggregated: VWAP, moving avg)
      ↓
DuckDB Lakehouse (ducklake extension)
      ↓
Metabase Dashboard
```

---

## 4. Required Tech Stack (all new vs Project 3)

| Component | Technology | Notes |
|---|---|---|
| Data source | Coinbase WebSocket (market_trades channel) | Public, no auth required |
| Message broker | RabbitMQ | Runs in Docker |
| Landing DB | PostgreSQL | Runs in Docker, OLTP |
| Transformation | dbt (PostgreSQL adapter) | Medallion: Bronze/Silver/Gold |
| Lakehouse | DuckDB + ducklake extension | OLAP, isolated from Postgres |
| BI Dashboard | Metabase | Runs in Docker |
| Orchestration | Docker Compose (multi-container stack) | All services in one file |
| Language | Python 3.12+ | websockets, pika (RabbitMQ), psycopg2 |

---

## 5. Key Concepts to Know

**Why RabbitMQ?**  
The WebSocket produces data faster than PostgreSQL can write. RabbitMQ acts as a buffer — if Postgres goes down, messages queue safely in RabbitMQ instead of being lost.

**Why DuckDB separate from PostgreSQL?**  
Analysts running heavy aggregation queries (VWAP over hours of data) would lock tables in PostgreSQL and cause missed trades. DuckDB is a read-optimized OLAP database — same data, no lock conflicts.

**Medallion Architecture (dbt):**
- Bronze = raw JSON, untyped, as-is from Postgres
- Silver = parsed JSON, typed columns (timestamp, float for price/size), deduplicated by trade_id
- Gold = aggregated business metrics (1-minute windows, VWAP, trade count, high/low)

**VWAP = Volume Weighted Average Price:**
```
VWAP = SUM(price * size) / SUM(size)
```
The standard metric for a "fair price" in a time window.

---

## 6. Project 3 Lessons Applied to Project 4

| Lesson from P3 | How to apply in P4 |
|---|---|
| Use `@dataclass(frozen=True)` for config | Same pattern for DB, RabbitMQ, DuckDB config |
| Exponential backoff on API calls | Apply to WebSocket reconnect logic |
| Cursor context manager (`with conn.cursor()`) | Use everywhere in Postgres writes |
| DRY — extract shared logic | Single consumer base class, not copy-pasted handlers |
| `client_session_keep_alive` for long connections | WebSocket needs reconnect logic for same reason |
| Imports at top of file | Always |
| No `auto_create_table` — define schema explicitly | Create Bronze table DDL explicitly |

---

## 7. Environment Setup

- **OS:** Windows 11 / PowerShell
- **Docker:** Docker Desktop installed and working (v28.5.1)
- **uv:** Installed and working
- **Snowflake account:** nfsqmyv-ce67328 (NOT used in Project 4 — this uses PostgreSQL)
- **New `.env` needed** for: PostgreSQL credentials, RabbitMQ credentials, DuckDB path, Coinbase symbols

---

## 8. Assistant Instructions

- Always start by reading this file before doing any work
- When in doubt about the working style, refer to section 2
- Do not run commands — show them and wait for confirmation
- For new technologies (RabbitMQ, DuckDB, Metabase), explain the concept in Spanish before writing code
- Keep a `study.md` updated in Spanish explaining what has been built and why
- After each major milestone, remind the student to commit
- Check for linter errors after every file edit
