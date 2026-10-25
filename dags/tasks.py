from airflow.decorators import task
from aiflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from config import SNOWFLAKE_CONN_ID

@task
def run_sql(file_path: str):
    with open(file_path, 'r') as f:
        sql = f.read()

    hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    hook.run(sql)