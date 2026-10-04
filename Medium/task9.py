''' Background Checks '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(background_checks):
    res = background_checks.withColumns({
        "crime_count": F.size(F.split(F.col("criminal_record"), ",")),
        "jobs_count": F.size(F.split(F.col("employment_history"), ",")),
        "degrees_count": F.size(F.split(F.col("education_history"), ",")),
        "places_lived_count": F.size(F.split(F.col("address"), ",")),
    }).select(
        "check_id", "full_name", "dob", "crime_count", "jobs_count", "degrees_count", "places_lived_count"
    )

    return res