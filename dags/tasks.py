from airflow.decorators import task
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from config import SNOWFLAKE_CONN_ID

@task
def run_sql(sql_path: str = '', sql_query: str = '' , get_first: bool = False):
    if sql_path:
        with open(sql_path, 'r') as f:
            sql = f.read()
    elif sql_query:
        sql = sql_query
    else:
        raise ValueError("Either 'sql_path' or 'sql_query' has not been provided correctly.")

    hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)

    if get_first:
        result = hook.get_first(sql)
        if not result or result[0] is None:
            raise ValueError(f"Procedure {sql} did not return a valid row count")
        return int(result[0])
    else:
        hook.run(sql)   