''' Mortgage Interest Rates '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(MortgageDetails, UserMortgages):
    res = MortgageDetails.join(
        UserMortgages,
        on="MortgageID",
        how="inner"
    ).groupBy(
        "MortgageType"
    ).agg(
        F.sum("InterestRate").alias("TotalRates"),
        F.count("UserId").alias("UserID").alias("TotalUsers")
    ).withColumn(
        "RateOfMortgage", F.col("TotalRates")/F.col("TotalUsers")
    ).select(
        "MortgageType", "RateOfMortgage"
    )

    return res