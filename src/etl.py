"""
================================================================================
ETL Module — Data Warehouse Sales
================================================================================
Description : Contains all data generation and loading functions for populating
              the sales data warehouse. Each function follows the pattern:
              generate_*() builds the records list, load_*() inserts into the DB.

Tables populated:
    - dim_date     : Calendar dates for the year 2023 with holiday flags (BR).
    - dim_customer : 100 synthetic customer profiles generated via Faker.
    - dim_product  : 50 randomly generated product records across 4 categories.
    - fact_sales   : 10,000 synthetic sales transactions.

Author      : Roland Garcia
Created     : 2026-01-01
================================================================================
"""

# ---------------------------------------------------------------------------
# Standard library
# ---------------------------------------------------------------------------
import logging
import random

# ---------------------------------------------------------------------------
# Third-party
# ---------------------------------------------------------------------------
import holidays
import pandas as pd
from faker import Faker
from sqlalchemy import insert, select
from sqlalchemy.engine import Engine

# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------
from models import dim_customer, dim_date, dim_product, fact_sales

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PRODUCT_CATALOG: dict[str, list[str]] = {
    "Electronics": [
        "Notebook", "Smartphone", "Tablet", "Monitor", "Keyboard",
        "Headphone", "Webcam", "SSD", "USB Hub", "Charger",
    ],
    "Furniture": [
        "Standing Desk", "Office Chair", "Bookshelf", "Filing Cabinet",
        "Lamp", "Whiteboard", "Monitor Stand", "Drawer", "Couch", "Table",
    ],
    "Clothing": [
        "T-Shirt", "Jacket", "Sneakers", "Cap", "Backpack",
        "Hoodie", "Pants", "Socks", "Belt", "Gloves",
    ],
    "Sports": [
        "Yoga Mat", "Dumbbell", "Resistance Band", "Jump Rope", "Water Bottle",
        "Gym Bag", "Knee Pad", "Foam Roller", "Pull-up Bar", "Stopwatch",
    ],
}

DATE_RANGE_START = "2023-01-01"
DATE_RANGE_END   = "2023-12-31"
HOLIDAY_COUNTRY  = "BR"

NUM_CUSTOMERS    = 100
NUM_PRODUCTS     = 50
NUM_SALES        = 10_000


# ===========================================================================
# Date dimension
# ===========================================================================

def generate_date_records() -> list[dict]:
    """
    Generate a list of daily date records for the configured date range.

    Each record includes calendar attributes and Brazilian holiday flags.

    Returns:
        list[dict]: One record per day between DATE_RANGE_START and DATE_RANGE_END.
    """
    dates = pd.date_range(start=DATE_RANGE_START, end=DATE_RANGE_END, freq="D")
    br_holidays = holidays.country_holidays(HOLIDAY_COUNTRY)

    return [
        {
            "date_id":     int(date.strftime("%Y%m%d")),
            "date":        date.date(),
            "day":         date.day,
            "month":       date.month,
            "quarter":     date.quarter,
            "year":        date.year,
            "day_of_week": date.weekday(),
            "is_weekend":  date.weekday() >= 5,
            "is_holiday":  date.date() in br_holidays,
        }
        for date in dates
    ]


def load_dim_dates(engine: Engine) -> None:
    """
    Populate the dim_date table with calendar records for the year 2023.

    Args:
        engine (Engine): SQLAlchemy engine connected to the target database.
    """
    records = generate_date_records()
    with engine.connect() as conn:
        conn.execute(insert(dim_date), records)
        conn.commit()
    logging.info("dim_date loaded: %d records.", len(records))


# ===========================================================================
# Customer dimension
# ===========================================================================

def generate_customer_records() -> list[dict]:
    """
    Generate a list of synthetic customer records using the Faker library.

    Returns:
        list[dict]: NUM_CUSTOMERS synthetic customer profiles.
    """
    fake = Faker()
    return [
        {
            "customer_name":  fake.name(),
            "customer_email": fake.email(),
            "city":           fake.city(),
            "country":        fake.country(),
            "is_corporate":   random.choice([True, False]),
        }
        for _ in range(NUM_CUSTOMERS)
    ]


def load_customer_records(engine: Engine) -> None:
    """
    Populate the dim_customer table with synthetic customer data.

    Args:
        engine (Engine): SQLAlchemy engine connected to the target database.
    """
    records = generate_customer_records()
    with engine.connect() as conn:
        conn.execute(insert(dim_customer), records)
        conn.commit()
    logging.info("dim_customer loaded: %d records.", len(records))


# ===========================================================================
# Product dimension
# ===========================================================================

def generate_product_records() -> list[dict]:
    """
    Generate a list of random product records from the predefined catalog.

    Products are selected randomly across all categories with randomized prices.

    Returns:
        list[dict]: NUM_PRODUCTS product records.
    """
    records = []
    for i in range(NUM_PRODUCTS):
        category = random.choice(list(PRODUCT_CATALOG.keys()))
        product_name = random.choice(PRODUCT_CATALOG[category])
        records.append({
            "product_name": product_name,
            "category":     category,
            "price":        round(random.uniform(50, 5000), 2),
        })
    return records


def load_products_records(engine: Engine) -> None:
    """
    Populate the dim_product table with randomly generated product data.

    Args:
        engine (Engine): SQLAlchemy engine connected to the target database.
    """
    records = generate_product_records()
    with engine.connect() as conn:
        conn.execute(insert(dim_product), records)
        conn.commit()
    logging.info("dim_product loaded: %d records.", len(records))


# ===========================================================================
# Sales fact table
# ===========================================================================

def generate_facts_sales_records(
    date_ids: list[int],
    customer_ids: list[int],
    product_ids: list[int],
) -> list[dict]:
    """
    Generate a list of synthetic sales transaction records.

    Args:
        date_ids     (list[int]): Valid date_id values from dim_date.
        customer_ids (list[int]): Valid customer_id values from dim_customer.
        product_ids  (list[int]): Valid product_id values from dim_product.

    Returns:
        list[dict]: NUM_SALES sales transaction records.
    """
    records = []
    for _ in range(NUM_SALES):
        quantity     = random.randint(1, 10)
        unit_price   = round(random.uniform(50, 5000), 2)
        total_amount = round(quantity * unit_price, 2)
        records.append({
            "date_id":      random.choice(date_ids),
            "customer_id":  random.choice(customer_ids),
            "product_id":   random.choice(product_ids),
            "quantity":     quantity,
            "unit_price":   unit_price,
            "total_amount": total_amount,
        })
    return records


def load_facts_sales(engine: Engine) -> None:
    """
    Populate the fact_sales table with synthetic sales transactions.

    Fetches valid foreign key IDs from all dimension tables before generating
    and inserting the fact records.

    Args:
        engine (Engine): SQLAlchemy engine connected to the target database.
    """
    with engine.connect() as conn:
        date_ids     = [row[0] for row in conn.execute(select(dim_date.c.date_id))]
        customer_ids = [row[0] for row in conn.execute(select(dim_customer.c.customer_id))]
        product_ids  = [row[0] for row in conn.execute(select(dim_product.c.product_id))]

        records = generate_facts_sales_records(date_ids, customer_ids, product_ids)
        conn.execute(insert(fact_sales), records)
        conn.commit()
    logging.info("fact_sales loaded: %d records.", len(records))
