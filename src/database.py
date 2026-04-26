import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL


def get_engine():
    load_dotenv()

    url_object = URL.create(
        "postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 5432)),
    )

    return create_engine(url_object)