''' Social Media PII '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(input_df):
	res = input_df.select(
        F.regexp_replace("phone", "^\\d{6}", "******").alias("anon_phone"),
        F.substring_index("email", "@", -1).alias("email_domain"),
        "user_id"
    ).drop("email", "phone")
	
	return res