''' Call Center '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(calls_df, customers_df):
	res = calls_df.join(
        customers_df,
        on="cust_id",
        how="inner"
    ).groupBy(
        "date"
    ).agg(
        F.countDistinct("cust_id").alias("num_customers"),
        F.sum("duration").alias("total_duration")
    )
	
	return res