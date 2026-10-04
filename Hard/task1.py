''' Property Management Company '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(properties_df, landlords_df):
	res = properties_df.join(
        landlords_df,
        on="landlord_id",
        how="left"
    ).groupBy(
        "landlord_id",
        F.concat_ws(" ", "first_name", "last_name").alias("landlord_name")
    ).agg(
        F.sum("rent").alias("total_rental_income")
    )
	
	return res