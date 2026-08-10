import os
from airflow.decorators import dag, task
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from datetime import datetime
from config import SNOWFLAKE_CONN_ID, FOLDER_ORDER, SNOWFLAKE_OBJECTS_DIR

@dag(
    dag_id='airlines_dwh_pipeline',
    start_date=datetime(2026, 1, 1),
    schedule='@daily',
    catchup=False
)
def setup_db():
    @task
    def run_sql(file_path: str):
        with open(file_path, 'r') as f:
            sql = f.read()

        hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
        hook.run(sql)

    previous_task = None

    for folder_name in FOLDER_ORDER:
        folder_path = os.path.join(SNOWFLAKE_OBJECTS_DIR, folder_name)

        if not os.path.isdir(folder_path):
            continue

        for file_name in os.listdir(folder_path):
            if not file_name.endswith('.sql'):
                continue

            file_path = os.path.join(folder_path, file_name)
            task_id = f"{folder_name}-{file_name.replace('.sql', '')}"
            current_task = run_sql.override(task_id=task_id)(file_path)

            if previous_task is not None:
                previous_task >> current_task

            previous_task = current_task

setup_db()