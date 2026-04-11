# Project 4 — Technical Profile & Coach Questions

---

## 1. Code Quality Standards (target level)

This is an academic project simulating industry patterns. Apply these standards:

### Configuration
- `@dataclass(frozen=True)` for all config classes (Postgres, RabbitMQ, DuckDB)
- All secrets in `.env`, never hardcoded
- `.env.example` provided with placeholder values

### Error Handling
- WebSocket producer: automatic reconnect with exponential backoff
- RabbitMQ consumer: manual message acknowledgment (`basic_ack`) — only ack after successful Postgres write
- Postgres writes: retry on `OperationalError` (connection lost)
- All errors logged with `loguru`, never silenced

### Code Structure
```
project4_crypto/
├── src/
│   ├── config.py          # @dataclass configs for all services
│   ├── producer.py        # WebSocket → RabbitMQ
│   ├── consumer.py        # RabbitMQ → PostgreSQL (Bronze)
│   ├── lakehouse_job.py   # Gold (Postgres) → DuckDB
│   └── __init__.py
├── dbt_project/           # Bronze → Silver → Gold models
│   ├── models/
│   │   ├── silver/
│   │   └── gold/
│   └── dbt_project.yml
├── docker-compose.yml     # RabbitMQ + PostgreSQL + Metabase
├── pyproject.toml
├── .env.example
└── main.py                # Orchestrator (start producer + consumer)
```

### Testing
- dbt built-in tests: `not_null`, `unique` on trade_id in Silver
- dbt custom test: `assert_price_positive.sql`
- Python: manual smoke test (run producer for 30s, verify rows in Postgres)

### Security (academic-appropriate)
- No hardcoded credentials anywhere
- RabbitMQ: credentials from `.env` (not default guest/guest in production)
- PostgreSQL: dedicated user with limited permissions (not superuser)
- `.gitignore` covers: `.env`, DuckDB files (`*.duckdb`), Postgres data volumes

---

## 2. Architecture Patterns

### Producer (WebSocket → RabbitMQ)
```python
# Pattern: daemon with reconnect loop
while True:
    try:
        async with websockets.connect(WS_URL) as ws:
            await subscribe(ws, symbols=["BTC-USD", "ETH-USD"])
            async for message in ws:
                channel.basic_publish(exchange='', routing_key=QUEUE, body=message)
    except Exception:
        logger.warning("Connection lost, retrying in {n}s...")
        await asyncio.sleep(backoff)
```

### Consumer (RabbitMQ → PostgreSQL)
```python
# Pattern: manual ack — message only removed from queue after successful DB write
def callback(ch, method, properties, body):
    try:
        insert_to_postgres(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

### dbt Silver — Key transformation
```sql
-- Parse JSON, cast types, deduplicate by trade_id
select distinct on (trade_id)
    (raw_payload->>'trade_id')::bigint       as trade_id,
    (raw_payload->>'product_id')::text       as symbol,
    (raw_payload->>'price')::numeric(18,8)   as price,
    (raw_payload->>'size')::numeric(18,8)    as size,
    (raw_payload->>'time')::timestamptz      as traded_at,
    (raw_payload->>'side')::text             as side
from {{ source('bronze', 'bronze_trades') }}
```

### dbt Gold — VWAP per minute
```sql
-- 1-minute tumbling windows
select
    date_trunc('minute', traded_at) as window_start,
    symbol,
    count(*)                        as trade_count,
    sum(price * size) / sum(size)   as vwap,
    min(price)                      as low_price,
    max(price)                      as high_price,
    sum(size)                       as total_volume
from {{ ref('silver_trades') }}
group by 1, 2
```

---

## 3. Key Libraries (new in Project 4)

| Library | Purpose | Install |
|---|---|---|
| `websockets` | Async WebSocket client for Coinbase | `uv add websockets` |
| `pika` | RabbitMQ client (AMQP protocol) | `uv add pika` |
| `psycopg2-binary` | PostgreSQL connector | `uv add psycopg2-binary` |
| `dbt-postgres` | dbt adapter for PostgreSQL | `uv add dbt-postgres` |
| `duckdb` | DuckDB embedded database | `uv add duckdb` |
| `asyncio` | Built-in — for async WebSocket loop | stdlib |

---

## 4. Docker Compose Services Needed

```yaml
services:
  rabbitmq:
    image: rabbitmq:3.13-management
    ports: ["5672:5672", "15672:15672"]  # 15672 = management UI
    
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: crypto_db
      POSTGRES_USER: crypto_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports: ["5432:5432"]
    
  metabase:
    image: metabase/metabase:latest
    ports: ["3000:3000"]
    depends_on: [postgres]
```

---

## 5. Questions for the Coach

### Architecture & Scope
1. **Coinbase authentication:** The WebSocket market_trades channel — is it truly public with no API key required, or do we need a Coinbase Advanced Trade API key?
2. **Symbols:** Which cryptocurrency pairs are required? BTC-USD only, or multiple (ETH-USD, SOL-USD)? This affects the producer filter logic and Gold aggregations.
3. **Bronze schema:** Should Bronze store the raw JSON as a single `JSONB` column in Postgres, or should we parse it immediately into typed columns? The spec says "raw, untyped JSON data" which suggests JSONB.
4. **Ducklake vs DuckDB:** The spec mentions "ducklake extension" specifically. Is this the new `ducklake` extension (requires DuckDB 1.2+) or standard DuckDB with Parquet files? These have very different setups.

### dbt & Transformation
5. **dbt profiles:** Should dbt connect to PostgreSQL locally, or is there a shared instance for the class?
6. **Gold layer refresh rate:** How often should the lakehouse job run? Every minute, every 5 minutes? This determines whether to use a lightweight scheduler (APScheduler) or a full Airflow DAG.
7. **Historical data:** Do we need to backfill historical trades, or is the pipeline strictly forward-looking (only live data from when the producer starts)?

### Metabase
8. **Metabase connection:** Should Metabase connect to DuckDB or PostgreSQL Gold layer? The spec says "pointed directly at the Ducklake" but Metabase's native DuckDB support is limited — is a Parquet file or a DuckDB file acceptable?
9. **Dashboard requirements:** Are there specific visualizations required (e.g., price chart, VWAP line, volume bars), or is the content left to the student?

### Presentation & Deliverables
10. **Fault tolerance demo:** The spec says to "briefly turn off the Postgres container to show RabbitMQ queuing." Should this be live during the presentation or acceptable as a pre-recorded video clip?
11. **Repository:** Should this be a new repository or a branch of the Project 3 repo?
12. **Team size:** The spec says "2-3 people" but also says "Individual Architecture Project" — is this truly individual or can we pair?

---

## 6. Risk Areas to Watch

| Risk | Mitigation |
|---|---|
| WebSocket drops connection frequently | Implement reconnect loop from day 1 |
| Coinbase rate limits | Use a single connection, not multiple |
| RabbitMQ queue grows unbounded | Set `x-max-length` on queue as safety |
| DuckDB file locked during Metabase query | Open DuckDB in read-only mode in Metabase |
| `distinct on` not supported by all DBs | PostgreSQL supports it; standard SQL alternative is `ROW_NUMBER()` |
| Docker Compose port conflicts with Project 3 | Project 3 used port 8501; Project 4 uses 5432, 5672, 15672, 3000 — no conflict |
