from airflow.decorators import dag
from datetime import datetime
from config import STAGE2_PROCEDURE, AUDIT_TABLE, STAGE3_PROCEDURE
from sql import POPULATE_STAGE1, LOG_STAGE2_AUDIT, LOG_STAGE3_AUDIT
from tasks import run_sql

@dag(
    dag_id='populate_dag',
    start_date=datetime(2026, 1, 1),
    schedule='@daily',
    catchup=False
)
def populate_db():
    stage1 = run_sql.override(task_id="populate_stage1")(POPULATE_STAGE1)
    stage2_rows = run_sql.override(task_id="run_stage2_procedure")(f"CALL { STAGE2_PROCEDURE };", get_first=True)
    stage3_rows = run_sql.override(task_id="run_stage3_procedure")(f"CALL { STAGE3_PROCEDURE };", get_first=True)
    log_stage2 = run_sql.override(task_id="log_stage2_audit")(LOG_STAGE2_AUDIT.format(audit_table=AUDIT_TABLE, rows=stage2_rows))
    log_stage3 = run_sql.override(task_id="log_stage3_audit")(LOG_STAGE3_AUDIT.format(audit_table=AUDIT_TABLE, rows=stage3_rows))


    stage1 >> stage2_rows >> log_stage2 >> stage3_rows >> log_stage3

populate_db()