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


def load_products(engine):
    """Load a fixed set of sample products into the products staging table."""
    with engine.connect() as conn:
        conn.execute(insert(dim_product), [
            {"product_name": "Notebook", "category": "Electronics", "price": 4599.99},
            {"product_name": "Wireless Mouse", "category": "Electronics", "price": 149.90},
            {"product_name": "Standing Desk", "category": "Furniture", "price": 2200.00},
            {"product_name": "USB-C Hub", "category": "Electronics", "price": 299.90},
            {"product_name": "Office Chair", "category": "Furniture", "price": 1800.00},
        ])
        conn.commit()


def generate_product_records():
    """
    Generate a list of 50 random product records across multiple categories.

    Returns:
        list[dict]: 50 product records with product_name, category, and price.
    """
    produtos_por_categoria = {
        "Electronics": ["Notebook", "Smartphone", "Tablet", "Monitor", "Keyboard", "Headphone", "Webcam", "SSD",
                        "USB Hub", "Charger"],
        "Furniture": ["Standing Desk", "Office Chair", "Bookshelf", "Filing Cabinet", "Lamp", "Whiteboard",
                      "Monitor Stand", "Drawer", "Couch", "Table"],
        "Clothing": ["T-Shirt", "Jacket", "Sneakers", "Cap", "Backpack", "Hoodie", "Pants", "Socks", "Belt", "Gloves"],
        "Sports": ["Yoga Mat", "Dumbbell", "Resistance Band", "Jump Rope", "Water Bottle", "Gym Bag", "Knee Pad",
                   "Foam Roller", "Pull-up Bar", "Stopwatch"]
    }

    records = []
    for i in range(50):
        category = random.choice(list(produtos_por_categoria.keys()))
        product_name = random.choice(produtos_por_categoria[category])
        registro = {"product_name": product_name,
                    "category": category,
                    "price": round(random.uniform(50, 5000), 2)}
        records.append(registro)
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


def generate_customer_records():
    """
    Generate a list of 100 synthetic customer records using the Faker library.

    Returns:
        list[dict]: 100 customer records with name, email, city, country, and corporate flag.
    """
    fake = Faker()
    records = []
    for i in range(100):
        registro = {"customer_name": fake.name(),
                    "customer_email": fake.email(),
                    "city": fake.city(),
                    "country": fake.country(),
                    "is_corporate": random.choice([True, False]),}
        records.append(registro)
    return records


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


def generate_date_record():
    """
    Generate daily date records for the year 2023 with Brazilian holiday flags.

    Returns:
        list[dict]: One record per day in 2023 with calendar and holiday attributes.
    """
    datas = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    br_holidays = holidays.country_holidays("BR")
    records = []
    for date in datas:
        registro = {"date_id": int(date.strftime("%Y%m%d")),
                    "date": date.date(),
                    "day": date.day,
                    "month": date.month,
                    "quarter": date.quarter,
                    "year": date.year,
                    "day_of_week": date.weekday(),
                    "is_weekend": date.weekday() >= 5,
                    "is_holiday": date.date() in br_holidays
                    }
        records.append(registro)
    return records


def load_dim_dates(engine: Engine) -> None:
    """
    Populate the dim_date table with calendar records for the year 2023.

    Args:
        engine (Engine): SQLAlchemy engine connected to the target database.
    """
    records = generate_date_record()
    with engine.connect() as conn:
        conn.execute(insert(dim_date), records)
        conn.commit()


def generate_facts_sales_records(date_ids, customer_ids, product_ids):
    """
    Generate a list of 10,000 synthetic sales transaction records.

    Args:
        date_ids     (list): Valid date_id values from dim_date.
        customer_ids (list): Valid customer_id values from dim_customer.
        product_ids  (list): Valid product_id values from dim_product.

    Returns:
        list[dict]: 10,000 sales transaction records.
    """
    records = []
    for i in range(10000):
        quantity = random.randint(1, 10)
        unit_price = round(random.uniform(50, 5000), 2)
        total_amount = round(quantity * unit_price, 2)
        registro = {
            "date_id": random.choice(date_ids),
            "customer_id": random.choice(customer_ids),
            "product_id": random.choice(product_ids),
            "quantity": quantity,
            "unit_price": unit_price,
            "total_amount": total_amount,
        }
        records.append(registro)
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
