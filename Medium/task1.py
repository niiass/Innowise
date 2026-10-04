''' CRM SAAS Company '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(customers, orders, products):
    res = orders.join(
        customers,
        on="customer_id",
        how="left"
    ).join(
        products,
        on="product_id",
        how="left"
    ).select(
        "category",
        F.concat_ws(" ", "first_name", "last_name").alias("customer_name"),
        "email",
        "order_date",
        "order_id",
        "product_name"
    )
    
    return res