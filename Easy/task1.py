''' Streaming Platform '''


from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(input_df):
    res = input_df.filter((input_df.view_count > 1000000) & (input_df.release_year >= 2019))
    
    return res