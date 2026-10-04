''' Mining Corporation '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(mines, extraction):
	res = mines.join(
        extraction,
        on=(mines.id == extraction.mine_id),
        how="left"
    ).groupBy(
        "location", "mineral"
    ).agg(
        F.sum("quantity").alias("total_quantity")
    )
	
	return res