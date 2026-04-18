"""
COVID-19 Intelligence Dashboard
Connects directly to Snowflake MARTS schema.
Run with: uv run streamlit run streamlit/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import snowflake.connector
from dotenv import load_dotenv

from src.config import snowflake as sf_config

load_dotenv()

st.set_page_config(
    page_title="COVID-19 Intelligence Platform",
    page_icon="🦠",
    layout="wide",
)

# ── Snowflake connection ──────────────────────────────────────────────────────

@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=sf_config.account,
        user=sf_config.user,
        password=sf_config.password,
        warehouse=sf_config.warehouse,
        database=sf_config.database,
        role=sf_config.role,
        client_session_keep_alive=True,
    )


@st.cache_data(ttl=3600)
def query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetch_pandas_all()


def build_state_filter(selected: list, column: str = "state_fips") -> str:
    """Build a SQL AND clause for state filtering with input validation."""
    safe = [s for s in selected if str(s).isdigit()]
    if not safe:
        return ""
    return f"AND {column} IN ({','.join(repr(s) for s in safe)})"


# ── Sidebar ───────────────────────────────────────────────────────────────────

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "View",
    ["Overview", "Geographic", "Metrics Deep Dive", "Data Quality"],
)

st.sidebar.divider()

# State filter — used by CFR and Hospitalization Rate metrics
all_states = query("""
    SELECT DISTINCT state_fips
    FROM COVID_DB.MARTS.MART_CASE_FATALITY_RATE
    ORDER BY state_fips
""")["STATE_FIPS"].tolist()

selected_states = st.sidebar.multiselect(
    "Filter by State (FIPS)",
    options=all_states,
    default=[],
    placeholder="All states",
)

st.sidebar.divider()
st.sidebar.caption("COVID-19 Intelligence Platform")
st.sidebar.caption("Data: CDC + US Census")

# ── Page: Overview ────────────────────────────────────────────────────────────

if page == "Overview":
    st.title("🦠 COVID-19 Intelligence Platform")
    st.markdown("**National Public Health Analytics Consortium** — Data Engineering Project 3")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    total_cases = query("SELECT SUM(total_cases) as v FROM COVID_DB.MARTS.MART_CASES_PER_100K")["V"].iloc[0]
    total_deaths = query("SELECT SUM(total_deaths) as v FROM COVID_DB.MARTS.MART_CASE_FATALITY_RATE")["V"].iloc[0]
    avg_cfr = query("SELECT AVG(case_fatality_rate_pct) as v FROM COVID_DB.MARTS.MART_CASE_FATALITY_RATE WHERE case_fatality_rate_pct > 0")["V"].iloc[0]
    counties = query("SELECT COUNT(DISTINCT county_fips) as v FROM COVID_DB.MARTS.MART_CASES_PER_100K")["V"].iloc[0]

    col1.metric("Total Cases", f"{int(total_cases or 0):,}")
    col2.metric("Total Deaths", f"{int(total_deaths or 0):,}")
    col3.metric("Avg Case Fatality Rate", f"{float(avg_cfr or 0):.2f}%")
    col4.metric("Counties Covered", f"{int(counties or 0):,}")

    st.divider()

    st.subheader("National Case Trend — 3-Month Rolling Average by State")
    df_trend = query("""
        SELECT state_fips, case_month, rolling_3mo_avg_cases
        FROM COVID_DB.MARTS.MART_ROLLING_AVG_CASES
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
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

# ── Page: Geographic ──────────────────────────────────────────────────────────

elif page == "Geographic":
    st.title("🗺️ Geographic Analysis")
    st.divider()

    st.subheader("Cases per 100k Population by County")
    df_geo = query("""
        SELECT county_fips, county_name, state_fips,
               SUM(cases_per_100k) as total_cases_per_100k
        FROM COVID_DB.MARTS.MART_CASES_PER_100K
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
        st.plotly_chart(fig, width="stretch")

    st.subheader("Vaccination Coverage vs Case Rate by County")
    df_vacc = query("""
        SELECT county_fips, state_abbrev, county_name,
               pct_series_complete, cumulative_cases_per_100k
        FROM COVID_DB.MARTS.MART_VACCINATION_VS_CASES
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
                "CUMULATIVE_CASES_PER_100K": "Cases per 100k",
            },
            opacity=0.6,
        )
        st.plotly_chart(fig2, width="stretch")

# ── Page: Metrics Deep Dive ───────────────────────────────────────────────────

elif page == "Metrics Deep Dive":
    st.title("📊 Metrics Deep Dive")
    st.divider()

    metric = st.selectbox(
        "Select a metric to explore",
        [
            "Case Fatality Rate by State",
            "Cases per 100k — Top Counties",
            "Booster Adoption Rate by State",
            "Hospitalization Rate by State ★",
            "Severity Index — Top Counties ★",
        ],
    )

    if metric == "Case Fatality Rate by State":
        st.markdown("**Deaths / Confirmed Cases × 100** — highlights regional healthcare capacity differences.")
        state_filter = build_state_filter(selected_states)
        df_cfr = query(f"""
            SELECT state_fips, case_month, case_fatality_rate_pct
            FROM COVID_DB.MARTS.MART_CASE_FATALITY_RATE
            WHERE case_fatality_rate_pct BETWEEN 0 AND 20
            {state_filter}
            ORDER BY case_month
        """)
        if not df_cfr.empty:
            fig = px.line(
                df_cfr,
                x="CASE_MONTH",
                y="CASE_FATALITY_RATE_PCT",
                color="STATE_FIPS",
                title="Case Fatality Rate (%) Over Time by State",
                labels={"CASE_FATALITY_RATE_PCT": "CFR %", "CASE_MONTH": "Month"},
            )
            fig.update_layout(showlegend=len(selected_states) > 0)
            st.plotly_chart(fig, width="stretch")

    elif metric == "Cases per 100k — Top Counties":
        st.markdown("**Population-normalized case rate** — enables fair comparison across counties of different sizes.")
        df_top = query("""
            SELECT county_name, state_fips, SUM(cases_per_100k) as total
            FROM COVID_DB.MARTS.MART_CASES_PER_100K
            GROUP BY 1, 2
            ORDER BY total DESC
            LIMIT 25
        """)
        if not df_top.empty:
            fig = px.bar(
                df_top,
                x="TOTAL",
                y="COUNTY_NAME",
                orientation="h",
                color="STATE_FIPS",
                title="Top 25 Counties by Cumulative Cases per 100k",
                labels={"TOTAL": "Cases per 100k", "COUNTY_NAME": "County"},
            )
            fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, width="stretch")

    elif metric == "Booster Adoption Rate by State":
        st.markdown("**Booster doses / population** — measures ongoing vaccine engagement beyond initial series.")
        df_boost = query("""
            SELECT state_abbrev, AVG(pct_boosted) as avg_pct_boosted
            FROM COVID_DB.MARTS.MART_VACCINATION_VS_CASES
            WHERE state_abbrev IS NOT NULL
            GROUP BY 1
            ORDER BY avg_pct_boosted DESC
        """)
        if not df_boost.empty:
            fig = px.bar(
                df_boost,
                x="STATE_ABBREV",
                y="AVG_PCT_BOOSTED",
                title="Average Booster Adoption Rate by State",
                labels={"AVG_PCT_BOOSTED": "% Boosted", "STATE_ABBREV": "State"},
                color="AVG_PCT_BOOSTED",
                color_continuous_scale="Blues",
            )
            st.plotly_chart(fig, width="stretch")

    elif metric == "Hospitalization Rate by State ★":
        st.markdown(
            "**Custom metric** — hospitalizations / confirmed cases × 100, by state and month. "
            "Signals healthcare system burden independently of fatality rate. "
            "A high hospitalization rate with a low CFR indicates strong ICU care; "
            "high in both signals an overwhelmed system."
        )
        state_filter = build_state_filter(selected_states)
        df_hosp = query(f"""
            SELECT state_fips, case_month, hospitalization_rate_pct, total_cases
            FROM COVID_DB.MARTS.MART_HOSPITALIZATION_RATE
            WHERE hospitalization_rate_pct BETWEEN 0 AND 100
            {state_filter}
            ORDER BY case_month
        """)
        if not df_hosp.empty:
            fig = px.line(
                df_hosp,
                x="CASE_MONTH",
                y="HOSPITALIZATION_RATE_PCT",
                color="STATE_FIPS",
                title="Hospitalization Rate (%) Over Time by State",
                labels={
                    "HOSPITALIZATION_RATE_PCT": "Hospitalization Rate %",
                    "CASE_MONTH": "Month",
                },
            )
            fig.update_layout(showlegend=len(selected_states) > 0)
            st.plotly_chart(fig, width="stretch")

    elif metric == "Severity Index — Top Counties ★":
        st.markdown(
            "**Custom metric** — composite severity score per county: "
            "hospitalization rate × 0.4 + ICU rate × 0.4 + case fatality rate × 0.2. "
            "Combines three clinical indicators into a single ranking to support "
            "resource allocation decisions by public health officials."
        )
        df_sev = query("""
            SELECT county_fips, county_name, state_fips,
                   severity_index, hosp_rate_pct, icu_rate_pct, cfr_pct, total_cases
            FROM COVID_DB.MARTS.MART_SEVERITY_INDEX
            WHERE severity_index > 0
            ORDER BY severity_index DESC
            LIMIT 30
        """)
        if not df_sev.empty:
            fig = px.bar(
                df_sev,
                x="SEVERITY_INDEX",
                y="COUNTY_NAME",
                orientation="h",
                color="SEVERITY_INDEX",
                color_continuous_scale="OrRd",
                hover_data=["STATE_FIPS", "HOSP_RATE_PCT", "ICU_RATE_PCT", "CFR_PCT", "TOTAL_CASES"],
                title="Top 30 Counties by Severity Index",
                labels={"SEVERITY_INDEX": "Severity Index", "COUNTY_NAME": "County"},
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, width="stretch")

# ── Page: Data Quality ────────────────────────────────────────────────────────

elif page == "Data Quality":
    st.title("✅ Data Quality & Pipeline Health")
    st.divider()

    st.subheader("Source Freshness")
    df_fresh = query("SELECT * FROM COVID_DB.MARTS.MART_DATA_FRESHNESS ORDER BY SOURCE_TABLE")

    if not df_fresh.empty:
        for _, row in df_fresh.iterrows():
            status = row["FRESHNESS_STATUS"]
            color_map = {"Fresh": "green", "Recent": "blue", "Stale": "orange", "Very Stale": "red"}
            color = color_map.get(status, "gray")
            hours = int(row["HOURS_SINCE_LOAD"])
            st.markdown(
                f"**{row['SOURCE_NAME']}** (`{row['SOURCE_TABLE']}`) — "
                f"Last loaded: `{row['LAST_LOADED_AT']}` — "
                f":{color}[**{status}**] ({hours}h ago)"
            )

    st.divider()
    st.subheader("dbt Test Results")
    st.info(
        "19 tests configured — 18 PASS, 1 WARN (duplicate county_fips in vaccinations — known, partial load).\n\n"
        "Custom tests validate:\n"
        "- Cases per 100k is never negative\n"
        "- Case fatality rate is between 0% and 100%\n"
        "- All case records are from 2020 or later"
    )
