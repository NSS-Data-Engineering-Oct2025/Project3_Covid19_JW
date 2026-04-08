"""
COVID-19 Intelligence Dashboard (Enhanced)
Run with: uv run streamlit run streamlit/app.py
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="COVID-19 Intelligence Platform",
    page_icon="🦠",
    layout="wide",
)

# ── Config ────────────────────────────────────────────────────────────────────

DB = os.environ.get("SNOWFLAKE_DATABASE", "COVID_DB")
SCHEMA = os.environ.get("SNOWFLAKE_SCHEMA", "MARTS")

STATE_FIPS_MAP = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA",
    "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL",
    "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN",
    "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME",
    "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS",
    "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
    "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND",
    "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
    "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT",
    "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI",
    "56": "WY"
}

# ── Snowflake ─────────────────────────────────────────────────────────────────


@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=DB,
        role=os.environ.get("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
    )


@st.cache_data(ttl=3600)
def query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetch_pandas_all()

# ── Sidebar ───────────────────────────────────────────────────────────────────


st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "View",
    ["Overview", "Geographic", "Metrics Deep Dive", "Data Quality"],
)

# Load states
states_df = query(f"""
    SELECT DISTINCT state_fips
    FROM {DB}.{SCHEMA}.MART_CASES_PER_100K
    ORDER BY state_fips
""")

# Normalize + map
states_df["STATE_FIPS"] = states_df["STATE_FIPS"].astype(str).str.zfill(2)
states_df["STATE"] = states_df["STATE_FIPS"].map(STATE_FIPS_MAP)

# Legend
with st.sidebar.expander("State Legend"):
    legend_df = pd.DataFrame(
        [(k, v) for k, v in STATE_FIPS_MAP.items()],
        columns=["FIPS", "State"]
    )
    st.dataframe(legend_df, use_container_width=True)

st.sidebar.divider()
st.sidebar.caption("COVID-19 Intelligence Platform")
st.sidebar.caption("Data: CDC + US Census")

# ── Page: Overview ────────────────────────────────────────────────────────────

if page == "Overview":
    st.title("🦠 COVID-19 Intelligence Platform")
    st.divider()

    state_options = states_df["STATE"].dropna().tolist()

    select_all_states = st.checkbox("Select All States", value=True)

    if select_all_states:
        selected_states_geo_abbr = state_options
    else:
        selected_states_geo_abbr = st.multiselect(
            "Select States",
            state_options,
            default=state_options[:3]
        )

    if not selected_states_geo_abbr:
        st.warning("Please select at least one state")
        st.stop()

    reverse_map = {v: k for k, v in STATE_FIPS_MAP.items()}
    selected_states_geo = [reverse_map[s] for s in selected_states_geo_abbr]

    state_filter_geo = ",".join([f"'{s}'" for s in selected_states_geo])

    df_geo = query(f"""
        SELECT county_fips, county_name,
            SUM(cases_per_100k) as total_cases_per_100k
        FROM {DB}.{SCHEMA}.MART_CASES_PER_100K
        WHERE state_fips IN ({state_filter_geo})
        GROUP BY 1,2
    """)

    title_states = "All States" if select_all_states else ", ".join(
        selected_states_geo_abbr)

    col1, col2, col3, col4 = st.columns(4)

    kpi_df = query(f"""
    SELECT
        (SELECT SUM(total_cases)
         FROM {DB}.{SCHEMA}.MART_CASES_PER_100K
         WHERE state_fips IN ({state_filter_geo})) AS total_cases,

        (SELECT SUM(total_deaths)
         FROM {DB}.{SCHEMA}.MART_CASE_FATALITY_RATE
         WHERE state_fips IN ({state_filter_geo})) AS total_deaths,

        (SELECT AVG(case_fatality_rate_pct)
         FROM {DB}.{SCHEMA}.MART_CASE_FATALITY_RATE
         WHERE state_fips IN ({state_filter_geo})
           AND case_fatality_rate_pct > 0) AS avg_cfr,

        (SELECT COUNT(DISTINCT county_fips)
         FROM {DB}.{SCHEMA}.MART_CASES_PER_100K
         WHERE state_fips IN ({state_filter_geo})) AS counties
    """)

    row = kpi_df.iloc[0]

    col1.metric("Total Cases", f"{int(row['TOTAL_CASES'] or 0):,}")
    col2.metric("Total Deaths", f"{int(row['TOTAL_DEATHS'] or 0):,}")
    col3.metric("Avg CFR", f"{float(row['AVG_CFR'] or 0):.2f}%")
    col4.metric("Counties", f"{int(row['COUNTIES'] or 0):,}")

    st.divider()

    st.subheader("Case Trend (3-Month Rolling Avg)")
    df_trend = query(f"""
        SELECT state_fips, case_month, rolling_3mo_avg_cases
        FROM {DB}.{SCHEMA}.MART_ROLLING_AVG_CASES
        WHERE state_fips IN ({state_filter_geo})
        ORDER BY case_month
    """)

    df_trend["STATE_FIPS"] = df_trend["STATE_FIPS"].astype(str).str.zfill(2)
    df_trend["STATE"] = df_trend["STATE_FIPS"].map(STATE_FIPS_MAP)

    fig = px.line(
        df_trend,
        x="CASE_MONTH",
        y="ROLLING_3MO_AVG_CASES",
        color="STATE",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Severity Index by State (Average)")

    df_sev_top = query(f"""
        SELECT state_fips,
            AVG(severity_index) as avg_severity
        FROM {DB}.{SCHEMA}.MART_SEVERITY_INDEX
        WHERE state_fips IN ({state_filter_geo})
        GROUP BY state_fips
        ORDER BY avg_severity DESC
    """)

    df_sev_top["STATE_FIPS"] = df_sev_top["STATE_FIPS"].astype(
        str).str.zfill(2)
    df_sev_top["STATE"] = df_sev_top["STATE_FIPS"].map(STATE_FIPS_MAP)

    fig = px.bar(
        df_sev_top,
        x="STATE",
        y="AVG_SEVERITY",
        color="AVG_SEVERITY",
        title="Average Severity Index by State",
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Page: Geographic ──────────────────────────────────────────────────────────

elif page == "Geographic":
    st.title("🗺️ Geographic Analysis")
    st.divider()

    state_options = states_df["STATE"].dropna().tolist()

    select_all_states = st.checkbox("Select All States", value=True)

    if select_all_states:
        selected_states_geo_abbr = state_options
    else:
        selected_states_geo_abbr = st.multiselect(
            "Select States",
            state_options,
            default=state_options[:3]
        )

    if not selected_states_geo_abbr:
        st.warning("Please select at least one state")
        st.stop()

    reverse_map = {v: k for k, v in STATE_FIPS_MAP.items()}
    selected_states_geo = [reverse_map[s] for s in selected_states_geo_abbr]

    state_filter_geo = ",".join([f"'{s}'" for s in selected_states_geo])

    df_geo = query(f"""
        SELECT county_fips, county_name,
            SUM(cases_per_100k) as total_cases_per_100k
        FROM {DB}.{SCHEMA}.MART_CASES_PER_100K
        WHERE state_fips IN ({state_filter_geo})
        GROUP BY 1,2
    """)

    title_states = "All States" if select_all_states else ", ".join(
        selected_states_geo_abbr)

    fig = px.choropleth(
        df_geo,
        geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
        locations="COUNTY_FIPS",
        color="TOTAL_CASES_PER_100K",
        scope="usa",
        title=f"Cases per 100k — {title_states}",
    )
    st.plotly_chart(fig, use_container_width=True)

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
        st.markdown(
            "**Deaths / Confirmed Cases × 100** — highlights regional healthcare capacity differences.")
        df_cfr = query("""
            SELECT state_fips, case_month, case_fatality_rate_pct
            FROM COVID_DB.MARTS.MART_CASE_FATALITY_RATE
            WHERE case_fatality_rate_pct BETWEEN 0 AND 20
            ORDER BY case_month
        """)
        if not df_cfr.empty:
            df_cfr["STATE_FIPS"] = df_cfr["STATE_FIPS"].astype(
                str).str.zfill(2)
            df_cfr["STATE"] = df_cfr["STATE_FIPS"].map(STATE_FIPS_MAP)
            fig = px.line(
                df_cfr,
                x="CASE_MONTH",
                y="CASE_FATALITY_RATE_PCT",
                color="STATE",
                title="Case Fatality Rate (%) Over Time by State",
                labels={"CASE_FATALITY_RATE_PCT": "CFR %",
                        "CASE_MONTH": "Month"},
            )
            fig.update_layout(showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

    elif metric == "Cases per 100k — Top Counties":
        st.markdown(
            "**Population-normalized case rate** — enables fair comparison across counties of different sizes.")
        df_top = query("""
            SELECT county_name, state_fips, SUM(cases_per_100k) as total
            FROM COVID_DB.MARTS.MART_CASES_PER_100K
            GROUP BY 1, 2
            ORDER BY total DESC
            LIMIT 25
        """)
        if not df_top.empty:
            df_top["STATE_FIPS"] = df_top["STATE_FIPS"].astype(
                str).str.zfill(2)
            df_top["STATE"] = df_top["STATE_FIPS"].map(STATE_FIPS_MAP)
            fig = px.bar(
                df_top,
                x="TOTAL",
                y="COUNTY_NAME",
                orientation="h",
                color="STATE",
                title="Top 25 Counties by Cumulative Cases per 100k",
                labels={"TOTAL": "Cases per 100k", "COUNTY_NAME": "County"},
            )
            fig.update_layout(showlegend=True, yaxis={
                              "categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

    elif metric == "Booster Adoption Rate by State":
        st.markdown(
            "**Booster doses / population** — measures ongoing vaccine engagement beyond initial series.")
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
                labels={"AVG_PCT_BOOSTED": "% Boosted",
                        "STATE_ABBREV": "State"},
                color="AVG_PCT_BOOSTED",
                color_continuous_scale="Blues",
            )
            st.plotly_chart(fig, use_container_width=True)

    elif metric == "Hospitalization Rate by State ★":
        st.markdown(
            "**Custom metric** — hospitalizations / confirmed cases × 100, by state and month. "
            "Signals healthcare system burden independently of fatality rate."
        )
        df_hosp = query("""
            SELECT state_fips, case_month, hospitalization_rate_pct, total_cases
            FROM COVID_DB.MARTS.MART_HOSPITALIZATION_RATE
            WHERE hospitalization_rate_pct BETWEEN 0 AND 100
            ORDER BY case_month
        """)
        if not df_hosp.empty:
            df_hosp["STATE_FIPS"] = df_hosp["STATE_FIPS"].astype(
                str).str.zfill(2)
            df_hosp["STATE"] = df_hosp["STATE_FIPS"].map(STATE_FIPS_MAP)
            fig = px.line(
                df_hosp,
                x="CASE_MONTH",
                y="HOSPITALIZATION_RATE_PCT",
                color="STATE",
                title="Hospitalization Rate (%) Over Time by State",
                labels={
                    "HOSPITALIZATION_RATE_PCT": "Hospitalization Rate %",
                    "CASE_MONTH": "Month",
                },
            )
            fig.update_layout(showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

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
            WHERE total_cases >= 1
            ORDER BY severity_index DESC
        """)

        if df_sev.empty:
            st.warning("No data found.")
        else:
            df_sev.columns = [c.upper() for c in df_sev.columns]
            fig = px.bar(
                df_sev,
                x="SEVERITY_INDEX",
                y="COUNTY_NAME",
                orientation="h",
                color="SEVERITY_INDEX",
                color_continuous_scale="OrRd",
                hover_data=["STATE_FIPS", "HOSP_RATE_PCT",
                            "ICU_RATE_PCT", "CFR_PCT", "TOTAL_CASES"],
                title="Top 30 Counties by Severity Index",
                labels={"SEVERITY_INDEX": "Severity Index",
                        "COUNTY_NAME": "County"},
            )
            st.write(fig)
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

# ── Page: Data Quality ────────────────────────────────────────────────────────

elif page == "Data Quality":
    st.title("✅ Data Quality")
    st.divider()

    df_fresh = query(f"""
        SELECT source_name, freshness_status, hours_since_load
        FROM {DB}.{SCHEMA}.MART_DATA_FRESHNESS
    """)

    for _, row in df_fresh.iterrows():
        color = {
            "Fresh": "green",
            "Recent": "blue",
            "Stale": "orange",
            "Very Stale": "red"
        }.get(row["FRESHNESS_STATUS"], "gray")

        st.markdown(
            f"**{row['SOURCE_NAME']}** — "
            f":{color}[{row['FRESHNESS_STATUS']}] "
            f"({int(row['HOURS_SINCE_LOAD'])}h ago)"
        )

    st.divider()

    st.subheader("Validation Rules")

    st.markdown("""
    - Non-negative case metrics  
    - Valid percentage ranges (0–100%)  
    - Temporal consistency (post-2020 data only)  
    - Key integrity across dimensions  

    All checks enforced via dbt during pipeline execution.
    """)
