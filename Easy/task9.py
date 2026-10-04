''' Geology Samples '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(input_df):
	res = input_df.withColumn(
        "age", F.regexp_extract("description", r"(\d+)", 1)
    ).select(
        "age", "description", "sample_id"
    )
	
	return res