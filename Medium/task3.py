''' AI Research '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(research_papers, authors):
	rule = W.partitionBy("paper_id").orderBy("author_id")
	
	res = research_papers.join(
        authors,
        on="paper_id",
        how="left"
    ).withColumn(
        "row_number", F.dense_rank().over(rule)
    ).select(
        "author_id",
        "name",
        "paper_id",
        "row_number"
    )
	
	return res