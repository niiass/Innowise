''' Mountain Climbing '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(mountain_info, mountain_climbers):
	res = mountain_climbers.join(
        mountain_info,
        on=(mountain_climbers.mountain_name==mountain_info.name),
        how="left"
    ).withColumn(
        "rank", F.dense_rank().over(W.partitionBy(F.col("mountain_name")).orderBy(F.col("climb_date").desc()))
    ).where(
        F.col("rank")==1
    ).select(
        "climb_date", "climb_time", "climber_name", "mountain_name"
    )
	
	return res