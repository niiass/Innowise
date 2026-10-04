''' Private Equity Firms '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(pe_firms, pe_funds, pe_investments):
	res = pe_funds.join(
        pe_firms,
        on="firm_id",
        how="outer"
    ).join(
        pe_investments,
        on="fund_id",
        how="outer"
    ).dropna(how="all")
	
	return res