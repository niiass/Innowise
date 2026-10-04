''' Organizing Manufacturing Parts '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(df1, df2):
	res = df1.join(
        df2,
        on="product_id",
        how="inner"
    ).withColumn(
        "row_number", F.row_number().over(W.orderBy(F.col("manufacturing_date")))
    ).select(
        "*"
    )
	
	return res