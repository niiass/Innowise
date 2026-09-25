from datetime import datetime, date
import pandas as pd
from pyspark.sql import Row
from pyspark.sql import SparkSession
from config import URL, PROPERTIES
from pyspark.sql.functions import col, count, concat, lit, sum, concat_ws, dense_rank, when, unix_timestamp
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("PostgreSQL Connection with PySpark") \
    .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3") \
    .getOrCreate()

def task1(url: str, properties: dict):
    ''' Output the number of movies in each category, sorted in descending order. '''

    film_category = spark.read.jdbc(url=url, table="film_category", properties=properties)
    category = spark.read.jdbc(url=url, table="category", properties=properties)

    res = film_category.join(
        category,
        on="category_id",
        how="left"
    ).groupBy(
        category.name
    ).agg(
        count("film_id").alias("FilmCount")
    ).orderBy(
        col("FilmCount").desc()
    )

    res.show()

# task1(URL, PROPERTIES)

def task2(url: str, properties: dict):
    ''' Output the 10 actors whose movies rented the most, sorted in descending order. '''

    actor = spark.read.jdbc(url=url, table="actor", properties=properties)
    film_actor = spark.read.jdbc(url=url, table="film_actor", properties=properties)
    inventory = spark.read.jdbc(url=url, table="inventory", properties=properties)
    rental = spark.read.jdbc(url=url, table="rental", properties=properties)
    payment = spark.read.jdbc(url=url, table="payment", properties=properties)

    actor_inventory = film_actor.join(
        inventory,
        on="film_id",
        how="left"
    ).select(film_actor.actor_id, inventory.inventory_id)

    actor_rental = actor_inventory.join(
        rental,
        on="inventory_id",
        how="left"
    ).select(actor_inventory.actor_id, rental.rental_id)

    actor_total = actor_rental.join(
        payment,
        on="rental_id",
        how="left"
    ).groupBy(
        actor_rental.actor_id
    ).agg(
        sum("amount").alias("total_rented")
    ).orderBy(
        col("total_rented").desc()
    ).limit(10)

    res = actor_total.join(
        actor,
        on="actor_id",
        how="left"
    ).select(
        concat(actor.first_name, lit(" "), actor.last_name).alias("full_name"),
        actor_total.total_rented
    )

    res.show()

# task2(URL, PROPERTIES)

def task3(url: str, properties: dict):
    ''' Output the category of movies on which the most money was spent.  '''

    payment = spark.read.jdbc(url=url, table="payment", properties=properties)
    rental = spark.read.jdbc(url=url, table="rental", properties=properties)
    inventory = spark.read.jdbc(url=url, table="inventory", properties=properties)
    film_list = spark.read.jdbc(url=url, table="film_list", properties=properties)

    rental_payment = payment.join(
        rental,
        on="rental_id",
        how="left"
    ).select(payment.rental_id, payment.amount, rental.inventory_id)

    film_inventory_id = film_list.join(
        inventory,
        on=(film_list.fid == inventory.film_id),
        how="inner"
    ).select(film_list.fid, film_list.title, film_list.category, inventory.inventory_id)

    res = rental_payment.join(
        film_inventory_id,
        on="inventory_id",
        how="inner"
    ).groupBy(
        film_inventory_id.fid, film_inventory_id.title, film_inventory_id.category
    ).agg(
        sum(rental_payment.amount).alias("total_spent")
    ).orderBy(
        col("total_spent").desc()
    ).limit(1)

    res.show()

# task3(URL, PROPERTIES)

def task4(url: str, properties: dict):
    ''' Output the names of movies that are not in the inventory. '''

    film = spark.read.jdbc(url=url, table="film", properties=properties)
    inventory = spark.read.jdbc(url=url, table="inventory", properties=properties)

    res = film.join(
        inventory,
        on="film_id",
        how="left"
    ).where(
        col("inventory_id").isNull()
    ).select(
        col("title")
    )

    res.show()

# task4(URL, PROPERTIES)

def task5(url: str, properties: dict):
    ''' Output the top 3 actors who have appeared most in movies in the “Children” category. If several actors have the same number of movies, output all of them. '''

    film_actor = spark.read.jdbc(url=url, table="film_actor", properties=properties)
    film_list = spark.read.jdbc(url=url, table="film_list", properties=properties)
    actor = spark.read.jdbc(url=url, table="actor", properties=properties)

    actors_film_count = film_actor.join(
        film_list,
        on=(film_actor.film_id == film_list.fid),
        how="inner"
    ).where(
        col("category") == "Children"
    ).groupBy(
        "actor_id"
    ).agg(
        count("actor_id").alias("film_count")
    )

    window_rank = Window.orderBy(col("film_count").desc())

    ranked_actors = actors_film_count.select(
        col("actor_id"),
        col("film_count"),
        dense_rank().over(window_rank).alias("tier")
    )

    res = actor.join(
        ranked_actors,
        on="actor_id",
        how="inner"
    ).where(
        col("tier") <= 3
    ).select(
        concat_ws(" ", col("first_name"), col("last_name")).alias("full_name")
    )

    res.show()

# task5(URL, PROPERTIES)

def task6(url: str, properties: dict):
    ''' Output cities with the number of active and inactive customers (active - customer.active = 1). Sort by the number of inactive customers in descending order. '''

    customer_list = spark.read.jdbc(url=url, table="customer_list", properties=properties)
    customer = spark.read.jdbc(url=url, table="customer", properties=properties)

    res = customer_list.alias("cl").join(
        customer,
        on=(customer_list.id == customer.customer_id),
        how="left"
    ).groupBy(
        col("cl.city")
    ).agg(
        sum(when(col("active") == 1, 1).otherwise(0)).alias("actives"),
        sum(when(col("active") == 0, 1).otherwise(0)).alias("inactives")
    ).select(
        col("city"),
        col("actives"),
        col("inactives")
    ).orderBy(
        col("inactives").desc()
    )

    res.show()

# task6(URL, PROPERTIES)

def task7(url: str, properties: dict):
    ''' Output the category of movies that have the highest number of total rental hours in the cities (customer.address_id in this city), and that start with the letter “a”. Do the same for cities with a “-” symbol. '''

    rental = spark.read.jdbc(url=url, table="rental", properties=properties)
    inventory = spark.read.jdbc(url=url, table="inventory", properties=properties)
    film_list = spark.read.jdbc(url=url, table="film_list", properties=properties)
    customer_list = spark.read.jdbc(url=url, table="customer_list", properties=properties)

    rental_with_duration = rental.where(
        col("return_date").isNotNull() & col("rental_date").isNotNull()
    ).withColumn(
        "duration_hours",
        (unix_timestamp("return_date") - unix_timestamp("rental_date")) / 3600
    )

    base_df = rental_with_duration.join(
        inventory, on="inventory_id", how="inner"
    ).join(
        film_list.alias("fl"), inventory.film_id == col("fl.fid"), how="inner"
    ).join(
        customer_list.alias("cl"), rental.customer_id == col("cl.id"), how="inner"
    )

    with_a = base_df.where(
        col("cl.city").ilike("a%")
    ).groupBy(
        col("fl.category")
    ).agg(
        sum("duration_hours").alias("total_hours")
    ).select(
        col("total_hours"),
        col("fl.category")
    ).orderBy(
        col("total_hours").desc()
    ).limit(1)

    with_dash = base_df.where(
        col("cl.city").ilike("%-%")
    ).groupBy(
        col("fl.category")
    ).agg(
        sum("duration_hours").alias("total_hours")
    ).select(
        col("total_hours"),
        col("fl.category")
    ).orderBy(
        col("total_hours").desc()
    ).limit(1)

    res = with_a.union(with_dash)

    res.show()

task7(URL, PROPERTIES)