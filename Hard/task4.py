''' SEO Optimization '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(pages):
    max_seo_score = pages.agg(F.max("seo_score")).collect()[0][0]

    res = pages.withColumn(
        "rank", F.dense_rank().over(W.partitionBy(F.col("domain")).orderBy(F.col("seo_score").desc()))
    ).where(
        F.col("rank") == 1
    ).select(
        F.col("domain"),
        F.col("url").alias("highest_seo_page"),
        F.col("seo_score").alias("highest_seo_score"),
        F.when(F.col("seo_score")==max_seo_score, F.col("url")).otherwise(None).alias("overall_highest_page"),
        F.when(F.col("seo_score")==max_seo_score, F.col("seo_score")).otherwise(None).alias("overall_highest_score")
    )
    
    return res