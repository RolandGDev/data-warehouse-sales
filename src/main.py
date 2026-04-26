from database import get_engine
from etl import load_products, query_products

engine = get_engine()
query_products(engine, "Electronics")
print("Concluido com sucesso!")