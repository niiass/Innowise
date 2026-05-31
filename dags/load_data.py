from airflow.decorators import dag, task
from airflow.sdk import Asset
import pandas as pd
from config import ASSET_FILE_PATH, MONGO_COLLECTION, MONGO_DB, PROCESSED_REVIEWS_FILE_PATH
from tasks import load_to_mongodb

@dag(
    dag_id='load_in_mongo',
    schedule=[Asset(ASSET_FILE_PATH)],
    catchup=False
)
def load_in_mongo():
    @task
    def csv_to_mongodb():
        load_to_mongodb(MONGO_COLLECTION, MONGO_DB, PROCESSED_REVIEWS_FILE_PATH)
    
    csv_to_mongodb()

load_in_mongo()
