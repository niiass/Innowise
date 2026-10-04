''' Running Payroll '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(employees, payroll):
	res = employees.join(
        payroll,
        on="employee_id",
        how="left"
    ).withColumn(
        "pay", 
        F.when(
            F.col("hours_worked") <= 40, F.col("hours_worked") * F.col("hourly_rate")
        ).otherwise(
            40 * F.col("hourly_rate") + (F.col("hours_worked") - 40) * F.col("hourly_rate") * 1.5
        )
    ).select(
        "employee_id",
        "name",
        "pay",
        "position"
    )
	
	return res