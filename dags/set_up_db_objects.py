import os
from airflow.decorators import dag
from datetime import datetime
from config import FOLDER_ORDER, SNOWFLAKE_OBJECTS_DIR
from tasks import run_sql

@dag(
    dag_id='set_up_db_objects',
    start_date=datetime(2026, 1, 1),
    schedule='@daily',
    catchup=False
)
def setup_db():
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