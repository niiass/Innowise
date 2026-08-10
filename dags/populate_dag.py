import os
from airflow.decorators import dag, task
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from datetime import datetime
from config import STAGE2_PROCEDURE, AUDIT_TABLE, STAGE3_PROCEDURE, SNOWFLAKE_CONN_ID, FOLDER_ORDER, SNOWFLAKE_OBJECTS_DIR
from sql import POPULATE_STAGE1, LOG_STAGE2_AUDIT, LOG_STAGE3_AUDIT

@dag(
    dag_id='airlines_dwh_populate',
    start_date=datetime(2026, 1, 1),
    schedule='@daily',
    catchup=False
)
def populate_db():
    @task
    def load_stage1():
        hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
        hook.run(POPULATE_STAGE1)

    @task
    def load_stage2():
        hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
        result = hook.get_first(f"CALL { STAGE2_PROCEDURE };")
        return int(result[0])

    @task
    def log_stage2_audit(rows_inserted: int):
        hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
        sql = LOG_STAGE2_AUDIT.format(audit_table=AUDIT_TABLE, rows=rows_inserted)
        hook.run(sql)

    @task
    def load_stage3():
        hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
        result = hook.get_first(f"CALL { STAGE3_PROCEDURE };")
        return int(result[0])

    @task
    def log_stage3_audit(rows_inserted: int):
        hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
        sql = LOG_STAGE3_AUDIT.format(audit_table=AUDIT_TABLE, rows=rows_inserted)
        hook.run(sql)

    stage1 = load_stage1()
    stage2_rows = load_stage2()
    stage3_rows = load_stage3()

    stage1 >> stage2_rows
    log_stage2_audit(stage2_rows) >> stage3_rows
    log_stage3_audit(stage3_rows)

populate_db()