''' Consumer Goods Discount Confusion '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(df):
    discount = F.regexp_extract(F.col("Description"), r"\[(\d+)% off\]", 1)

    res = df.withColumn(
        "Discount",
        F.when(discount != "", (discount/100.0)).otherwise(0.0)
    )
    return res