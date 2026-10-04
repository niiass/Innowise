''' Food and Beverage Sales '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(products, sales, inventory):
    total_sales = sales.groupBy(
        "product_id"
    ).agg(
        F.sum("quantity").alias("total_quantity"),
        F.sum("revenue").alias("total_revenue"),
    )

    total_stock = inventory.groupBy(
        "product_id"
    ).agg(
        F.sum("stock").alias("total_stock")
    )
    
    res = products.join(
        total_sales,
        on="product_id",
        how="left"
    ).join(
        total_stock,
        on="product_id",
        how="left"
    ).fillna(0).select(
        "category", "name", "product_id", "total_quantity", "total_revenue", "total_stock"
    )

    return res