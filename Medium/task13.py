''' Factory Duplicates '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(products_df, manufacturing_processes_df):
    products_distinct = products_df.dropDuplicates()
    manufacturing_processes_distinct = manufacturing_processes_df.dropDuplicates()

    res = products_distinct.join(
        manufacturing_processes_distinct,
        on="ProductID",
        how="left"
    )

    return res