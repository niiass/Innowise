from airflow.sensors.filesystem import FileSensor
from airflow.decorators import dag, task, task_group
from airflow.operators.bash import BashOperator
from airflow.sdk import Asset
import pandas as pd
import logging
from config import INPUT_REVIEWS_FILE_PATH, PROCESSED_REVIEWS_FILE_PATH, ASSET_FILE_PATH
from tasks import sort_dataset, remove_characters, replace_nulls

@dag(
    dag_id='process_tiktok_reviews',
    schedule=None,
    catchup=False
)
def process_data():
    logging.info("Waiting for data file...")
    wait_for_data_file=FileSensor(
        task_id='wait_for_data_file',
        filepath=INPUT_REVIEWS_FILE_PATH,
        poke_interval=10,
        timeout=120,
        mode='reschedule'
    )

    @task.branch(task_id='file_isempty')
    def check_file_isempty(filepath: str):
        import os
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            logging.info("File found. Routing to data processing.")
            return 'data_processing.sort'
        logging.info("File is empty.")
        return None
    
    @task_group(group_id='data_processing')
    def data_processing(processed_filepath: str):
        @task
        def sort(sort_by):
            sort_dataset(processed_filepath, sort_by)

        @task
        def remove_chars(remove_from: str):
            remove_characters(processed_filepath, remove_from)
        
        @task(outlets=[Asset(ASSET_FILE_PATH)])
        def replace():
            replace_nulls(processed_filepath)


        sort('at') >> remove_chars('content') >> replace()
    
    wait_for_data_file >> check_file_isempty(INPUT_REVIEWS_FILE_PATH) >> data_processing(PROCESSED_REVIEWS_FILE_PATH)

process_data()
