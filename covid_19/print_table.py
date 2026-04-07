import os
import yaml
import pandas as pd
from tabulate import tabulate
from sqlalchemy import create_engine
from urllib.parse import quote_plus


# Load dbt profile
profile_path = os.path.expanduser("~/.dbt/profiles.yml")

with open(profile_path, "r") as f:
    profiles = yaml.safe_load(f)

# Set profile and target
profile_name = "covid_19"  # change if your profile has a different name
target_name = "dev"
target = profiles[profile_name]["outputs"][target_name]

# Extract Snowflake connection info
user = target["user"]
password = target.get("password") or os.getenv("SNOWFLAKE_PASSWORD")
account = target["account"]
warehouse = target["warehouse"]
database = target["database"]
schema = target["schema"]
role = target.get("role")

# Get table and limit from user
table_name = input(
    "Enter table name (RAW_COVID_CASES, RAW_VACCINATIONS, or RAW_POPULATION): ").strip()
limit_input = input("Number of rows to display (default 10): ").strip()
limit = int(limit_input) if limit_input else 10

# Optional: key columns for specific tables
key_columns_map = {
    "RAW_COVID_CASES": ["state_fips", "county_fips", "case_month", "monthly_cases", "rolling_3mo_avg_cases"],
    "RAW_VACCINATIONS": ["state_fips", "county_fips", "case_month", "vaccinated", "fully_vaccinated"]
}

# Query the table
query = f"SELECT * FROM {table_name} LIMIT {limit}"
# # URL-encode the password for special characters
encoded_password = quote_plus(password)
engine = create_engine(
    f"snowflake://{user}:{encoded_password}@{account}/{database}/{schema}?warehouse={warehouse}&role={role}"
)  # Needs Snowflake-SQLAlchemy plugin installed
raw_df = pd.read_sql(query, engine)

# Handle wide tables and truncate text
MAX_COLUMNS = 8
if len(raw_df.columns) > MAX_COLUMNS:
    column_df = raw_df.iloc[:, :MAX_COLUMNS].copy()
else:
    column_df = raw_df.copy()

# Truncate long text fields
truncated_df = column_df.copy()
for col in truncated_df.select_dtypes(include="string").columns:
    truncated_df[col] = truncated_df[col].str.slice(
        0, 20)  # first 20 characters

# Optional: reorder columns if keys exist
if table_name in key_columns_map:
    keys = [col for col in key_columns_map[table_name]
            if col in truncated_df.columns]
    remaining_cols = [col for col in truncated_df.columns if col not in keys]
    tables_df = truncated_df[keys + remaining_cols].copy()
else:
    tables_df = truncated_df.copy()

# Print formattded table
print(tabulate(tables_df, headers="keys", tablefmt="fancy_grid"))
