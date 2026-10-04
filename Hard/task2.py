''' Manufacturing Plant '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(products, sales):
	res = products.join(
        sales,
        on="product_id",
        how="inner"
    ).select(
        "category",
        "product_name",
        F.dense_rank().over(W.partitionBy("category").orderBy(F.col("revenue").desc())).alias("rank"),
        "revenue"
    )
	
	return res