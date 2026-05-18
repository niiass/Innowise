from airflow.sensors.filesystem import FileSensor
from airflow.decorators import dag, task, task_group
from airflow.operators.bash import BashOperator
from airflow.sdk import Asset
import pandas as pd

@dag(
    dag_id='process_tiktok_reviews',
    schedule=None,
    catchup=False
)
def process_tiktok_reviews():
    path = '/opt/airflow/data/tiktok_google_play_reviews.csv'
    processed_path = '/opt/airflow/data/processed_reviews.csv'

    wait_for_data_file=FileSensor(
        task_id='wait_for_data_file',
        filepath='data/tiktok_google_play_reviews.csv',
        poke_interval=10,
        timeout=120,
        mode='reschedule'
    )

    @task.branch(task_id='check_file_isempty')
    def check_file_isempty():
        import os
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return 'data_processing.sort'
        return 'log_empty_file'
    
    log_empty_file = BashOperator(
        task_id='log_empty_file',
        bash_command='echo "File is empty!"'
    )
    
    @task_group(group_id='data_processing')
    def data_processing():
        @task(task_id='sort')
        def sort():
            reviews = pd.read_csv(path)
            if 'at' not in reviews.columns:
                raise ValueError("Column 'at' does not exist!")
            reviews = reviews.sort_values(by='at')
            reviews.to_csv(processed_path, index=False)


        @task(task_id='remove_chars')
        def remove_chars():
            reviews = pd.read_csv(processed_path)
            if 'content' not in reviews.columns:
                raise ValueError("Column 'content' does not exist!")
            reviews['content'] = reviews['content'].str.replace(
                pat=r'[^\w\s.,!?\'"\-_();:]',
                repl='',
                regex=True
            )
            reviews.to_csv(processed_path, index=False)
        
        @task(task_id='replace', outlets=[Asset("file:///opt/airflow/data/processed_reviews.csv")])
        def replace():
            reviews = pd.read_csv(processed_path)
            reviews = reviews.replace("null", "-")
            reviews = reviews.fillna("-")
            reviews.to_csv(processed_path, index=False)


        sort() >> remove_chars() >> replace()
    
    wait_for_data_file >> check_file_isempty() >> [log_empty_file, data_processing()]

process_tiktok_reviews()
