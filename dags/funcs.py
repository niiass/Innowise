from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from config import SNOWFLAKE_CONN_ID

def get_hook() -> SnowflakeHook:
    return SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)