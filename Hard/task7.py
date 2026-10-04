''' Government Budgeting '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(budget_df, spending_df):
    budget_var = budget_df.groupBy(
        "Department"
    ).agg(
        F.variance(F.col("Budget")).cast("integer").alias("Budget_Variance")
    )
    
    spending_var = spending_df.groupBy(
        "Department"
    ).agg(
        F.variance(F.col("Spending")).cast("integer").alias("Spending_Variance")
    )

    res = budget_var.join(
        spending_var,
        on="Department",
        how="inner"
    )

    return res