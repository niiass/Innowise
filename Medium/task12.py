''' Busy Airline '''

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Window as W
import pyspark
import datetime
import json

spark = SparkSession.builder.appName('run-pyspark-code').getOrCreate()

def etl(flights, airports, planes):
    origins = airports.alias("origins")
    destinations = airports.alias("destinations")

    origins_length = flights.join(
        origins,
        on=(flights.origin_airport == origins.airport_id),
        how="inner"
    ).select(
        "flight_id",
        F.length(F.col("airport_name")).alias("origin_airport_name_length")
    )

    destinations_length = flights.join(
        destinations,
        on=(flights.destination_airport == destinations.airport_id),
        how="inner"
    ).select(
        "flight_id",
        F.length(F.col("airport_name")).alias("destination_airport_name_length")
    )

    res = origins_length.join(
        destinations_length,
        on="flight_id",
        how="left"
    ).join(
        planes,
        on=(origins_length.flight_id==planes.plane_id),
        how="left"
    ).withColumn(
        "plane_model_length", F.length(F.col("plane_model"))
    ).drop(
        "plane_id", "plane_model"
    )

    return res