from sqlalchemy import insert, select
from models import products


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

def query_products(engine, category):
    with engine.connect() as conn:
        result = conn.execute(
            select(products).where(products.c.category == category)
        )
        for row in result:
            print(row)