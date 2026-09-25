import os
from dotenv import load_dotenv

load_dotenv(override=True)

user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
port = os.getenv("PORT")
db = os.getenv("DB")

URL = f"jdbc:postgresql://{host}:{port}/{db}"
PROPERTIES = {
    "user": user,
    "password": password,
    "driver": "org.postgresql.Driver"
}