''' Movies '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(movies_df):
	res = movies_df.where(F.col("box_office_collection").isNull())
	
	return res