''' VC Firms '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(companies, investments):
	res = companies.join(
        investments,
        on="company_id",
        how="left"
    ).groupBy(
        "industry"
    ).agg(
        F.sum("amount").alias("total_investment")
    )
	
	return res