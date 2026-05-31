from airflow.decorators import dag
from airflow.providers.snowflake.operators.snowflake import SQLExecuteQueryOperator
from datetime import datetime
from config import STAGE2_PROCEDURE, AUDIT_TABLE, STAGE3_PROCEDURE

@dag(
    dag_id='airlines_dwh_pipeline',
    start_date=datetime(2026, 1, 1),
    schedule='@daily',
    catchup=False,
    render_template_as_native_obj=True
)
def load_airlines_stages():
    load_stage2 = SQLExecuteQueryOperator(
        task_id='load_stage2',
        conn_id='snowflake_default',
        sql=f"CALL {STAGE2_PROCEDURE};"
    )

    log_stage2_audit = SQLExecuteQueryOperator(
        task_id='log_stage2_audit',
        conn_id='snowflake_default',
        sql="""
            INSERT INTO {audit_table} (PipelineName, SourceStage, TargetStage, RowsInserted)
            VALUES (
                'Populate stage2', 'stage1', 'stage2', {{{{ task_instance.xcom_pull(task_ids='load_stage2')[0][0] | int }}}}
            );
        """.format(audit_table=AUDIT_TABLE)
    )
    
    load_stage3 = SQLExecuteQueryOperator (
        task_id='load_stage3',
        conn_id='snowflake_default',
        sql=f"CALL {STAGE3_PROCEDURE};"
    )

    log_stage3_audit = SQLExecuteQueryOperator(
        task_id='log_stage3_audit',
        conn_id='snowflake_default',
        sql="""
            INSERT INTO {audit_table} (PipelineName, SourceStage, TargetStage, RowsInserted)
            VALUES (
            'Each Country Monthly Visitors', 'stage2', 'stage3', {{{{ task_instance.xcom_pull(task_ids='load_stage3')[0][0] | int }}}}
            );
        """.format(audit_table=AUDIT_TABLE)
    )
    
    load_stage2 >> log_stage2_audit >> load_stage3 >> log_stage3_audit

load_airlines_stages()