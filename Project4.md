### **Project 4 \- Individual Architecture Project: Real-Time Crypto Streaming & Lakehouse Analytics**

**Dataset:** Real-Time Coinbase Advanced Trade WebSocket (market\_trades channel)

**Team Size:** 2 \- 3

**Prerequisites:** Phase 5 complete \- Enterprise production deployment, operational excellence, and introductory orchestration mastery.

#### **🎯 Project Overview**

Build a complete, decoupled data engineering pipeline that ingests real-time cryptocurrency trades, buffers them through a message queue, and transforms them into an analytical lakehouse. This project bridges structured learning and the capstone, allowing you to demonstrate mastery of event-driven ingestion, the Medallion architecture (Bronze, Silver, Gold), and modern BI integrations.

#### **⚡ Important: Independent Technical Leadership**

This project demonstrates individual mastery of modern data flow patterns:

* **Decoupled Architecture:** Safely moving high-velocity data between services without bottlenecks.  
* **Data Modeling:** Designing a strict Bronze/Silver/Gold transformation pipeline using dbt.  
* **Lakehouse Concepts:** Separating the heavy-write transactional database from the read-optimized analytical engine.  
* **Production Excellence:** Running a multi-container stack locally using Docker Compose.

#### **📚 Business Context**

**Client:** A Boutique Quantitative Trading Firm

**Business Challenge:** The quantitative analysts need a real-time dashboard tracking the volatility and Volume Weighted Average Price (VWAP) of specific cryptocurrencies. They cannot query the production trading database directly because heavy analytical queries cause locked tables and missed trades.

**Your Mission:** You must build an event-driven pipeline that captures live trades from Coinbase, safely buffers them, lands them in a robust database, transforms the raw data, and exports the refined metrics into an isolated DuckDB "Lakehouse" for the analysts to query via Metabase.

#### **🏗️ Architecture & Implementation Requirements**

**The Required Technology Stack:**

1. **The Producer (Python \+ WebSockets):** A script that connects to the public Coinbase Advanced Trade WebSocket, filters for a specific cryptocurrency (e.g., BTC-USD), and pushes the raw JSON payload directly to a message broker.  
2. **The Broker (RabbitMQ):** A message queue that acts as a shock absorber, buffering the high-velocity trade data.  
3. **The Consumer (Python):** A continuous background worker that pulls messages from RabbitMQ and handles high-speed inserts into a PostgreSQL landing zone.  
4. **The Transformation Layer (PostgreSQL \+ dbt):** \* **Bronze:** Raw, untyped JSON data.  
   * **Silver:** Cleaned, deduplicated, and explicitly typed trade events.  
   * **Gold:** Aggregated business metrics (e.g., 1-minute tumbling windows, VWAP, moving averages).  
5. **The Lakehouse Job (Python/Orchestrator):** A scheduled job that extracts the Gold layer from PostgreSQL and writes it to a Ducklake.  
6. **The Analytics Layer (Metabase):** A BI dashboard pointed directly at the DuckDB lakehouse to visualize the crypto metrics.

#### **📅 Project Timeline & Independent Development**

**Ingestion & Buffering**

* **Environment Setup:** Create a docker-compose.yml spinning up RabbitMQ and PostgreSQL.  
* **Producer Script:** Write a Python daemon using websockets to connect to Coinbase and filter trades.  
* **Message Queuing:** Configure the Producer to drop the raw JSON payload onto a specific RabbitMQ queue.  
* **Day 1 Deliverables:** A running Docker stack and a working Python script successfully pushing live trades into RabbitMQ without dropping connection.

**Consumer Landing & Bronze Layer**

* **Consumer Script:** Write a Python worker that subscribes to the RabbitMQ queue.  
* **Postgres Ingestion:** Safely insert the raw JSON messages into a Postgres bronze\_trades table. Handle connection drops and optimize for write speed.  
* **Day 2 Deliverables:** A complete, decoupled stream. Data flows from Coinbase \-\> Python \-\> RabbitMQ \-\> Python \-\> Postgres continuously.

**Medallion Architecture via dbt**

* **dbt Initialization:** Connect dbt to your PostgreSQL instance.  
* **Silver Layer:** Write dbt models to parse the raw JSON, cast data types (timestamps, floats for price/volume), and handle any duplicate trade IDs.  
* **Gold Layer:** Write dbt models to aggregate the data into time-series metrics required by the business (VWAP, trade counts per minute, high/low tracking).  
* **Day 3 Deliverables:** A successfully executing dbt run that builds a clean Silver layer and an aggregated Gold layer in Postgres.

**The Lakehouse & BI Integration**

* **Lakehouse Export Job:** Write a Python script (or use a lightweight Airflow DAG) to extract the Gold data from Postgres and load it into Duckdb using the ducklake extension. .  
* **Metabase Setup:** Add Metabase to your Docker Compose stack and connect it to the Ducklake.  
* **Dashboarding:** Build out the required visual analytics for the quant team.  
* **Day 4 Deliverables:** An automated pipeline that updates DuckDB, and a finished Metabase dashboard displaying real-time aggregated crypto trends.

**Team Presentation**

* A 15-20 minute technical presentation and live demonstration (can be recorded video) 

#### **🎤 Individual Presentation Requirements**

**Architectural Reasoning**

* Explain the value of decoupling the WebSocket listener from the database using RabbitMQ.  
* Justify the use of the Medallion architecture.

**Technical Deep Dive**

* Showcase how you handled the JSON payload extraction in Python vs. dbt.  
* Explain your strategy for moving data from the Postgres OLTP system to the DuckDB OLAP lakehouse.

**Live System Demonstration (or video)** 

* Start the pipeline from scratch. Show the live data flowing into RabbitMQ, executing the dbt run, updating DuckDB, and refreshing Metabase.  
* Demonstrate fault tolerance (e.g., briefly turn off the Postgres container to show RabbitMQ queuing the messages safely).

**Q\&A**

* Professional defense of your architectural decisions and performance optimizations.

