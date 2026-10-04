''' E-Commerce Platform '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(products_df, orders_df):
	res = products_df.join(
        orders_df,
        on="product_id",
        how="inner"
    ).groupBy(
        "category"
    ).agg(
        F.avg("price").alias("avg_price"),
        F.count("quantity").alias("total_orders_count")
    )
	
	return res
