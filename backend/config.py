"""Configurations for the flask application."""
import os

API_KEY = os.environ["API_KEY"]
BASE_URL = "https://places.sit.ls.hereapi.com/places/v1/autosuggest"
POSTGRES_CONN = (
    f"postgresql://{os.environ['POSTGRES_USER']}"
    f":{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}"
    f":{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
)
