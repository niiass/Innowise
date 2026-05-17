from airflow.decorators import dag, task
from airflow.sdk import Asset
from airflow.providers.mongo.hooks.mongo import MongoHook
import pandas as pd

@dag(
    dag_id='load_in_mongo',
    schedule=[Asset("file:///opt/airflow/data/processed_reviews.csv")],
    catchup=False
)
def load_in_mongo():
    @task(task_id='csv_to_mongodb')
    def csv_to_mongodb():
        mongo_hook = MongoHook(mongo_conn_id='mongo_default')
        collection = mongo_hook.get_collection(mongo_collection='reviews', mongo_db='tiktok_reviews_db')
        data = pd.read_csv('/opt/airflow/data/processed_reviews.csv')
        data = data.to_dict(orient='records')
        collection.delete_many({})
        collection.insert_many(data)
    
    csv_to_mongodb()

load_in_mongo()
