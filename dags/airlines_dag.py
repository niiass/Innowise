from airflow.decorators import dag
from airflow.providers.snowflake.operators.snowflake import SQLExecuteQueryOperator
from datetime import datetime

@dag(
    dag_id='airlines_dwh_pipeline',
    start_date=datetime(2026, 1, 1),
    schedule='@daily',
    catchup=False,
    render_template_as_native_obj=True
)
def load_airlines_stages():
    load_stage2 = SQLExecuteQueryOperator(
        task_id='load_stage2_clean_airlines',
        conn_id='snowflake_default',
        sql="CALL innowise_snowflake_lms.stage2.load_clean_data();"
    )

    log_stage2_audit = SQLExecuteQueryOperator(
        task_id='load_stage2_audit_table',
        conn_id='snowflake_default',
        sql="""
            INSERT INTO innowise_snowflake_lms.stage2.audit (PipelineName, SourceStage, TargetStage, RowsInserted)
            VALUES (
                'Populate stage2', 'stage1', 'stage2', {{ task_instance.xcom_pull(task_ids='load_stage2_clean_airlines')[0][0] | int }}
            );
        """
    )
    
    load_stage3 = SQLExecuteQueryOperator (
        task_id='load_stage3_visitors_per_month',
        conn_id='snowflake_default',
        sql="CALL innowise_snowflake_lms.stage3.load_monthly_visitors();"
    )

    log_stage3_audit = SQLExecuteQueryOperator(
        task_id='stage3_data_insertion',
        conn_id='snowflake_default',
        sql="""
            INSERT INTO innowise_snowflake_lms.stage2.audit (PipelineName, SourceStage, TargetStage, RowsInserted)
            VALUES (
            'Each Country Monthly Visitors', 'stage2', 'stage3', {{ task_instance.xcom_pull(task_ids='load_stage3_visitors_per_month')[0][0] | int }}
            );
"""
    )
    
    load_stage2 >> log_stage2_audit >> load_stage3 >> log_stage3_audit

load_airlines_stages()