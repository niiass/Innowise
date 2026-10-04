''' Floors "R" Us '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(customers, orders, products):
    customers_sep = customers.select(
        "customer_id",
        "location",
        F.split(F.col("full_name"), " ").getItem(0).alias("first_name"),
        F.split(F.col("full_name"), " ").getItem(1).alias("last_name")
    )

    products_sep = products.select(
        "product_id",
        F.split(F.col("product_info"), ",").getItem(0).alias("product_type"),
        F.split(F.col("product_info"), ",").getItem(1).alias("product_color"),
    )

    res = orders.join(
        customers_sep, on="customer_id", how="inner"
    ).join(
        products_sep, on="product_id", how="inner"
    )

    return res