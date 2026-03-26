"""
COVID-19 Intelligence Dashboard
Connects directly to Snowflake MARTS schema.
Run with: streamlit run streamlit/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import snowflake.connector
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="COVID-19 Intelligence Platform",
    page_icon="🦠",
    layout="wide",
)

# ── Snowflake connection (cached) ────────────────────────────────────────────

@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.environ.get("SNOWFLAKE_DATABASE", "COVID_DB"),
        role=os.environ.get("SNOWFLAKE_ROLE", "SYSADMIN"),
    )


@st.cache_data(ttl=3600)
def query(_conn, sql: str) -> pd.DataFrame:
    return pd.read_sql(sql, _conn)


conn = get_connection()

# ── Sidebar ──────────────────────────────────────────────────────────────────

st.sidebar.title("Filters")
page = st.sidebar.radio(
    "View",
    ["Overview", "Geographic", "Metrics Deep Dive", "Data Quality"],
)

# ── Page: Overview ───────────────────────────────────────────────────────────

if page == "Overview":
    st.title("COVID-19 Intelligence Platform")
    st.markdown("National Public Health Analytics Consortium — Data Engineering Project 3")

    col1, col2, col3, col4 = st.columns(4)

    total_cases = query(conn, "SELECT SUM(total_cases) FROM MARTS.MART_CASES_PER_100K").iloc[0, 0]
    total_deaths = query(conn, "SELECT SUM(total_deaths) FROM MARTS.MART_CASE_FATALITY_RATE").iloc[0, 0]
    avg_cfr = query(conn, "SELECT AVG(case_fatality_rate_pct) FROM MARTS.MART_CASE_FATALITY_RATE WHERE case_fatality_rate_pct > 0").iloc[0, 0]
    counties_covered = query(conn, "SELECT COUNT(DISTINCT county_fips) FROM MARTS.MART_CASES_PER_100K").iloc[0, 0]

    col1.metric("Total Cases", f"{int(total_cases or 0):,}")
    col2.metric("Total Deaths", f"{int(total_deaths or 0):,}")
    col3.metric("Avg Case Fatality Rate", f"{float(avg_cfr or 0):.2f}%")
    col4.metric("Counties Covered", f"{int(counties_covered or 0):,}")

    st.divider()

    st.subheader("National Case Trend (Rolling 3-Month Average by State)")
    df_trend = query(conn, """
        SELECT state_fips, case_month, rolling_3mo_avg_cases
        FROM MARTS.MART_ROLLING_AVG_CASES
        ORDER BY case_month
    """)
    if not df_trend.empty:
        fig = px.line(
            df_trend,
            x="CASE_MONTH",
            y="ROLLING_3MO_AVG_CASES",
            color="STATE_FIPS",
            title="3-Month Rolling Average of New Cases by State",
            labels={"ROLLING_3MO_AVG_CASES": "Avg Cases", "CASE_MONTH": "Month"},
        )
        fig.update_traces(line=dict(width=1), opacity=0.7)
        st.plotly_chart(fig, use_container_width=True)

# ── Page: Geographic ─────────────────────────────────────────────────────────

elif page == "Geographic":
    st.title("Geographic Analysis")

    st.subheader("Cases per 100k Population by County")
    df_geo = query(conn, """
        SELECT county_fips, county_name, state_fips, SUM(cases_per_100k) as total_cases_per_100k
        FROM MARTS.MART_CASES_PER_100K
        GROUP BY 1, 2, 3
        ORDER BY total_cases_per_100k DESC
        LIMIT 500
    """)
    if not df_geo.empty:
        fig = px.choropleth(
            df_geo,
            geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
            locations="COUNTY_FIPS",
            color="TOTAL_CASES_PER_100K",
            color_continuous_scale="Reds",
            scope="usa",
            title="Cumulative Cases per 100k by County",
            labels={"TOTAL_CASES_PER_100K": "Cases per 100k"},
        )
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Vaccination Coverage vs Case Rate")
    df_vacc = query(conn, """
        SELECT county_fips, state_abbrev, county_name, pct_series_complete,
               cumulative_cases_per_100k
        FROM MARTS.MART_VACCINATION_VS_CASES
        WHERE pct_series_complete IS NOT NULL
          AND cumulative_cases_per_100k IS NOT NULL
        LIMIT 1000
    """)
    if not df_vacc.empty:
        fig2 = px.scatter(
            df_vacc,
            x="PCT_SERIES_COMPLETE",
            y="CUMULATIVE_CASES_PER_100K",
            color="STATE_ABBREV",
            hover_data=["COUNTY_NAME"],
            title="Vaccination Coverage vs Cumulative Cases per 100k",
            labels={
                "PCT_SERIES_COMPLETE": "% Series Complete",
                "CUMULATIVE_CASES_PER_100K": "Cumulative Cases per 100k",
            },
            opacity=0.6,
        )
        st.plotly_chart(fig2, use_container_width=True)

# ── Page: Metrics Deep Dive ──────────────────────────────────────────────────

elif page == "Metrics Deep Dive":
    st.title("Metrics Deep Dive")

    metric = st.selectbox(
        "Select Metric",
        ["Case Fatality Rate by State", "Cases per 100k — Top Counties", "Booster Adoption Rate"],
    )

    if metric == "Case Fatality Rate by State":
        df_cfr = query(conn, """
            SELECT state_fips, case_month, case_fatality_rate_pct
            FROM MARTS.MART_CASE_FATALITY_RATE
            WHERE case_fatality_rate_pct BETWEEN 0 AND 20
            ORDER BY case_month
        """)
        fig = px.line(
            df_cfr,
            x="CASE_MONTH",
            y="CASE_FATALITY_RATE_PCT",
            color="STATE_FIPS",
            title="Case Fatality Rate (%) Over Time by State",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif metric == "Cases per 100k — Top Counties":
        df_top = query(conn, """
            SELECT county_name, state_fips, SUM(cases_per_100k) as total
            FROM MARTS.MART_CASES_PER_100K
            GROUP BY 1, 2
            ORDER BY total DESC
            LIMIT 25
        """)
        fig = px.bar(
            df_top,
            x="TOTAL",
            y="COUNTY_NAME",
            orientation="h",
            title="Top 25 Counties by Cumulative Cases per 100k",
            color="STATE_FIPS",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif metric == "Booster Adoption Rate":
        df_boost = query(conn, """
            SELECT state_abbrev, AVG(pct_boosted) as avg_pct_boosted
            FROM MARTS.MART_VACCINATION_VS_CASES
            GROUP BY 1
            ORDER BY avg_pct_boosted DESC
        """)
        fig = px.bar(
            df_boost,
            x="STATE_ABBREV",
            y="AVG_PCT_BOOSTED",
            title="Average Booster Adoption Rate by State",
            labels={"AVG_PCT_BOOSTED": "% Boosted"},
        )
        st.plotly_chart(fig, use_container_width=True)

# ── Page: Data Quality ───────────────────────────────────────────────────────

elif page == "Data Quality":
    st.title("Data Quality & Pipeline Health")

    df_fresh = query(conn, "SELECT * FROM MARTS.MART_DATA_FRESHNESS ORDER BY SOURCE_TABLE")
    if not df_fresh.empty:
        st.subheader("Source Freshness")
        for _, row in df_fresh.iterrows():
            status = row["FRESHNESS_STATUS"]
            color = {"Fresh": "green", "Recent": "blue", "Stale": "orange", "Very Stale": "red"}.get(
                status, "gray"
            )
            st.markdown(
                f"**{row['SOURCE_NAME']}** (`{row['SOURCE_TABLE']}`) — "
                f"Last loaded: `{row['LAST_LOADED_AT']}` — "
                f":{color}[{status}] ({int(row['HOURS_SINCE_LOAD'])}h ago)"
            )

    st.divider()
    st.info(
        "Run `dbt test` from the Airflow DAG or CLI to see full test results. "
        "Check Airflow logs for pipeline execution history."
    )
