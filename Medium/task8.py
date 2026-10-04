''' Aerospace Equipment '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(aerospace_df, company_df):
	res = aerospace_df.join(
        company_df,
        on=(aerospace_df.company_id==company_df.id),
        how="inner"
    ).select(
        (aerospace_df.id).alias("id"),
        (aerospace_df.name).alias("equipment_name"),
        (aerospace_df.type).alias("equipment_type"),
        (aerospace_df.status).alias("equipment_status"),
        (company_df.name).alias("company_name"),
        (company_df.country).alias("country")
    ).withColumn(
        "status_label", 
        F.when(
            (F.col("country") == "USA") & (F.col("equipment_status") == "active"), "Domestic Active"
        ).when(
            (F.col("country") != "USA") & (F.col("equipment_status") == "active"), "Foreign Active"
        ).otherwise(
            "Inactive"
        )
    )
	
	return res