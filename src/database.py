"""
================================================================================
Database Module — Data Warehouse Sales
================================================================================
Description : Manages the SQLAlchemy engine creation for the PostgreSQL
              data warehouse. Credentials are loaded from a .env file
              using environment variables.

Author      : Roland Garcia
Created     : 2026-01-01
================================================================================
"""

# ---------------------------------------------------------------------------
# Standard library
# ---------------------------------------------------------------------------
import os

# ---------------------------------------------------------------------------
# Third-party
# ---------------------------------------------------------------------------
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Engine


def get_engine() -> Engine:
    """
    Create and return a SQLAlchemy engine connected to the PostgreSQL database.

    Credentials are read from environment variables loaded via a .env file:
    DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DB_PORT.

    Returns:
        Engine: A SQLAlchemy engine instance ready for database operations.

    Raises:
        sqlalchemy.exc.OperationalError: If the connection cannot be established.
    """
    load_dotenv()

    url = URL.create(
        "postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 5432)),
    )

    return create_engine(url)
