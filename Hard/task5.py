''' Customer Churn '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(df_accounts, df_activities, df_exit_surveys):
	res = df_activities.join(
        df_exit_surveys,
        on="user_id",
        how="left"
    ).join(
        df_accounts,
        on="user_id",
        how="left"
    ).dropDuplicates()
	
	return res