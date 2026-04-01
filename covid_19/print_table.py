import os
import yaml
import pandas as pd
from tabulate import tabulate
import snowflake.connector

# -----------------------------
# Load dbt profile
# -----------------------------
profile_path = os.path.expanduser("~/.dbt/profiles.yml")

with open(profile_path, "r") as f:
    profiles = yaml.safe_load(f)

# Assuming the target is 'dev' and profile is 'covid_19' (replace if needed)
profile_name = "covid_19"  # change if your profile has a different name
target_name = "dev"

# Direct access (will raise KeyError if missing)
target = profiles[profile_name]["outputs"][target_name]

# Extract connection info
user = target["user"]
password = target.get("password") or os.getenv("SNOWFLAKE_PASSWORD")
account = target["account"]
warehouse = target["warehouse"]
database = target["database"]
schema = target["schema"]
role = target.get("role")

# -----------------------------
# Connect to Snowflake
# -----------------------------
conn = snowflake.connector.connect(
    user=user,
    password=password,
    account=account,
    warehouse=warehouse,
    database=database,
    schema=schema,
    role=role
)

# -----------------------------
# Get table and limit from user
# -----------------------------
table_name = input("Enter table name (e.g., RAW_POPULATION): ")
limit = input("Number of rows to display (default 10): ")
limit = int(limit) if limit else 10

# -----------------------------
# Query and print table
# -----------------------------
query = f"SELECT * FROM {table_name} LIMIT {limit}"
tables_df = pd.read_sql(query, conn)
print(tabulate(tables_df, headers='keys', tablefmt='grid'))
