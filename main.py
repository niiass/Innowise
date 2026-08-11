import streamlit as st
import re

st.write("🧩 Snowflake DB Clone Tool")

conn = None
conn_error = None

try:
    conn = st.connection("snowflake")
except Exception as e:
    conn_error = str(e)

if conn_error:
    st.info(
        "No live Snowflake connection configured, so DB-existence checks and "
        "Execute SQL are disabled. You can still generate and copy the SQL. "
        f"(Connection error: {conn_error})"
    )

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_$]*$")

def valid_identifier(name: str) -> bool:
    return bool(IDENTIFIER_RE.match(name))

target_db_name = st.text_input("Target DB name").upper()
clone_from_db = st.text_input("Clone from DB").upper()
dev_role = st.text_input("Development role", value="DEVELOPMENT").upper()
read_only_role = st.text_input("Read-only role", value="READ_ONLY_ROLE").upper()

errors = []
if target_db_name and not valid_identifier(target_db_name):
    errors.append("Target DB name is not a valid Snowflake identifier.")
if clone_from_db and not valid_identifier(clone_from_db):
    errors.append("Clone from DB is not a valid Snowflake identifier.")
if read_only_role and not valid_identifier(read_only_role):
    errors.append("Read-only role is not a valid Snowflake identifier.")
for e in errors:
    st.error(e)

inputs_ready = bool(target_db_name and clone_from_db) and not errors

db_exists = False
existing_owner = None
if conn and target_db_name and valid_identifier(target_db_name):
    try:
        df = conn.query(f"SHOW DATABASES LIKE '{target_db_name}'", ttl=0)
        if len(df) > 0:
            db_exists = True
            existing_owner = df.iloc[0]["owner"] if "owner" in df.columns else "?"
    except Exception as e:
        st.warning(f"Could not check for existing databases: {e}")
 
if db_exists:
    st.warning(
        f"{target_db_name} already exists (owner: {existing_owner}). "
        "It will be dropped and recreated if you proceed."
    )

def dev_grants(db: str, role: str) -> str:
    return f"""
GRANT OWNERSHIP ON DATABASE {db} TO ROLE {role};
GRANT OWNERSHIP ON ALL SCHEMAS IN DATABASE {db} TO ROLE {role};
GRANT OWNERSHIP ON ALL TABLES IN DATABASE {db} TO ROLE {role};
GRANT OWNERSHIP ON ALL VIEWS IN DATABASE {db} TO ROLE {role};
GRANT OWNERSHIP ON ALL MATERIALIZED VIEWS IN DATABASE {db} TO ROLE {role};
GRANT OWNERSHIP ON ALL PROCEDURES IN DATABASE {db} TO ROLE {role};
GRANT OWNERSHIP ON ALL FUNCTIONS IN DATABASE {db} TO ROLE {role};

GRANT ALL PRIVILEGES ON FUTURE SCHEMAS IN DATABASE {db} TO ROLE {role};
GRANT ALL PRIVILEGES ON FUTURE TABLES IN DATABASE {db} TO ROLE {role};
GRANT ALL PRIVILEGES ON FUTURE VIEWS IN DATABASE {db} TO ROLE {role};
GRANT ALL PRIVILEGES ON FUTURE MATERIALIZED VIEWS IN DATABASE {db} TO ROLE {role};
GRANT ALL PRIVILEGES ON FUTURE PROCEDURES IN DATABASE {db} TO ROLE {role};
GRANT ALL PRIVILEGES ON FUTURE FUNCTIONS IN DATABASE {db} TO ROLE {role};
"""

def readonly_grants(db: str, role: str) -> str:
    return f"""
GRANT USAGE ON DATABASE {db} TO ROLE {role};
GRANT USAGE ON ALL SCHEMAS IN DATABASE {db} TO ROLE {role};
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE {db} TO ROLE {role};

GRANT SELECT ON ALL TABLES IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON FUTURE TABLES IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON ALL VIEWS IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON FUTURE VIEWS IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON ALL MATERIALIZED VIEWS IN DATABASE {db} TO ROLE {role};
GRANT SELECT ON FUTURE MATERIALIZED VIEWS IN DATABASE {db} TO ROLE {role};
"""

def build_full_sql() -> str:
    base_sql = (
        f"DROP DATABASE IF EXISTS {target_db_name};\n"
        f"CREATE DATABASE {target_db_name} CLONE {clone_from_db};"
    )
    dev_sql = dev_grants(target_db_name, dev_role)
    readonly_sql = readonly_grants(target_db_name, read_only_role)
    return f"{base_sql}\n\n{dev_sql}\n\n{readonly_sql}"

if "sql_query" not in st.session_state:
    st.session_state.sql_query = ""
 
if st.button("🔄 Refresh SQL", disabled=not inputs_ready):
    st.session_state.sql_query = build_full_sql()
 
st.markdown("## Generated SQL")
st.markdown("### Please, always check db names you set up!")

if st.session_state.sql_query:
    st.code(st.session_state.sql_query, language="sql")
else:
    st.caption("Fill in the fields above and click **Refresh SQL**.")


if st.button("🚀 Execute SQL", disabled=not (conn and st.session_state.sql_query)):
    statements = [s.strip() for s in st.session_state.sql_query.split(";") if s.strip()]
    try:
        session = conn.session()
        progress = st.progress(0, text="Running statements...")
        for i, stmt in enumerate(statements, start=1):
            session.sql(stmt).collect()
            progress.progress(i / len(statements), text=f"Ran statement {i}/{len(statements)}")
        st.success(f"Done - {len(statements)} statements executed successfully.")
    except Exception as e:
        st.error(f"Execution failed: {e}")
 
if not conn:
    st.caption("Execute SQL is disabled until a Snowflake connection is configured.")