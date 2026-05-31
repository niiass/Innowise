import pandas as pd
import logging
from airflow.providers.mongo.hooks.mongo import MongoHook
from config import INPUT_REVIEWS_FILE_PATH

def sort_dataset(processed_filepath, sort_by: str):
    logging.info("Sorting data.")
    reviews = pd.read_csv(INPUT_REVIEWS_FILE_PATH)
    if sort_by not in reviews.columns:
        raise ValueError(f"Column '{sort_by}' does not exist!")
    reviews = reviews.sort_values(by=sort_by)
    reviews.to_csv(processed_filepath, index=False)
    logging.info(f"Data sorted by column {sort_by} and saved changes successfully.")

def remove_characters(processed_filepath, remove_from: str):
    logging.info("Removing characters")
    reviews = pd.read_csv(processed_filepath)
    if remove_from not in reviews.columns:
        raise ValueError(f"Column '{remove_from}' does not exist!")
    reviews['content'] = reviews[remove_from].str.replace(
        pat=r'[^\w\s.,!?\'"\-_();:]',
        repl='',
        regex=True
    )
    reviews.to_csv(processed_filepath, index=False)
    logging.info(f"Characters filtered out from column {remove_from} and saved changes successfully.")

def replace_nulls(processed_filepath):
    logging.info("Replacing null and NaN values.")
    reviews = pd.read_csv(processed_filepath)
    reviews = reviews.replace("null", "-")
    reviews = reviews.fillna("-")
    reviews.to_csv(processed_filepath, index=False)
    logging.info("Nulls and NaNs were replaced with '-' and saved changes succesfully.")

def load_to_mongodb(collection: str, db :str, processed_filepath: str):
    mongo_hook = MongoHook(mongo_conn_id='mongo_default')
    collection = mongo_hook.get_collection(mongo_collection=collection, mongo_db=db)
    data = pd.read_csv(processed_filepath)
    data = data.to_dict(orient='records')
    collection.delete_many({})
    collection.insert_many(data)
