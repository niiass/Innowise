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
    def get_hook() -> SnowflakeHook:
        return SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)

    @task
    def load_table(sql: str):
        hook = get_hook()
        hook.run(sql)

    @task
    def run_procedure(procedure: str):
        hook = get_hook()
        result = hook.get_first(procedure)
        if not result or result[0] is None:
            raise ValueError(f"Procedure {procedure} did not return a valid row count")
        return int(result[0])

    @task
    def log_audit(audit_stage: str, rows: int):
        hook = get_hook()
        sql = audit_stage.format(audit_table=AUDIT_TABLE, rows=rows)
        hook.run(sql)

    stage1 = load_table(POPULATE_STAGE1)
    stage2_rows = run_procedure(f"CALL { STAGE2_PROCEDURE };")
    stage3_rows = run_procedure(f"CALL { STAGE3_PROCEDURE };")

    stage1 >> stage2_rows
    log_audit(LOG_STAGE2_AUDIT, stage2_rows) >> stage3_rows
    log_audit(LOG_STAGE3_AUDIT, stage3_rows)

populate_db()