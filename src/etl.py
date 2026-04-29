import random
import holidays
import pandas as pd
from sqlalchemy import insert, select
from models import products, dim_date, dim_customer, dim_product, fact_sales
from faker import Faker


def load_products(engine):
    with engine.connect() as conn:
        conn.execute(insert(products), [
            {"product_name": "Notebook", "category": "Electronics", "price": 4599.99},
            {"product_name": "Wireless Mouse", "category": "Electronics", "price": 149.90},
            {"product_name": "Standing Desk", "category": "Furniture", "price": 2200.00},
            {"product_name": "USB-C Hub", "category": "Electronics", "price": 299.90},
            {"product_name": "Office Chair", "category": "Furniture", "price": 1800.00},
        ])
        conn.commit()
def generate_product_records():
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

def load_products_records(engine):
    records = generate_product_records()
    with engine.connect() as conn:
        conn.execute(insert(dim_product), records)
        conn.commit()


def generate_customer_records():
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

def load_customer_records(engine):
    records = generate_customer_records()
    with engine.connect() as conn:
        conn.execute(insert(dim_customer), records)
        conn.commit()

def generate_date_record():
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

def load_dim_dates(engine):
    records = generate_date_record()
    with engine.connect() as conn:
        conn.execute(insert(dim_date), records)
        conn.commit()

def query_products(engine, category):
    with engine.connect() as conn:
        result = conn.execute(
            select(products).where(products.c.category == category)
        )
        for row in result:
            print(row)


def generate_facts_sales_records(date_ids, customer_ids, product_ids):

    records = []
    for i in range(10000):
        quantity = random.randint(1, 10) #inteiro entre 1 a 10
        unit_price = round(random.uniform(50, 5000), 2) #decimal entre 50 e 5000
        total_amount = round(quantity * unit_price, 2) #calculo inteiro
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

def load_facts_sales(engine):
    with engine.connect() as conn:
        date_ids     = [row[0] for row in conn.execute(select(dim_date.c.date_id))]
        customer_ids = [row[0] for row in conn.execute(select(dim_customer.c.customer_id))]
        product_ids  = [row[0] for row in conn.execute(select(dim_product.c.product_id))]
        records = generate_facts_sales_records(date_ids, customer_ids, product_ids)
        conn.execute(insert(fact_sales), records)
        conn.commit()